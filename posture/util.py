"""
miracle/posture/util.py

姿勢・ビートを構成する送信パーツ。socket を握って「組み立て→送信」する。

  - send_angle / send_rollpose / send_playmotion / send_controller … socket を毎回渡す raw 関数（単発用）。
  - Sender … socket を 1 回受け取り、以後 socket を渡さずにパーツを呼べるクラス。
             各関節の「現在角（最後に指令した角度）」を保持し、ビートの遷移計算に使う。
             ★ 状態を共有するため、Sender は呼び出し側で 1 個だけ作り、全 posture に渡す。

  - Sender.orient … Body/Head/Eye controller で向きを変える（playthisanglemotion とは別系統）。

motion id は「関節（part）」で決める＝1 関節 1 id。
  pose/up/down/back が同じ関節へ送るときは同じ id になり、後続が前を「置換」する
  （playthisanglemotion は id ごとに別 element として相対加算・保持されるため、
   id がフェーズ別だと積み重なって競合する。part 基準にして置換させる）。

ビートモデル: beat = 現在値 → (peak) → 目標(=その姿勢の resting 角度)。
  - beat 関節（beat_delta≠0）: angle → angle+delta×height（up）→ angle（down）で叩く。
  - 遷移関節（beat_delta=0 かつ 現在≠angle）: 現在 → 中間(EASE_IN, up) → angle(EASE_OUT, down)。
    ＝ロール差し出しのように「ビートしながら目的角へ運ぶ」。既に angle なら何もしない。

playthisaction は使わない（フェーズの timing は呼び出し側が刻む）。
"""
from __future__ import annotations

import json
import math
import socket
import threading

# socket への書き込みを直列化（複数スレッドからのビート送信に備える）
_send_lock = threading.Lock()


def _make_curve(slope0: float, slope1: float) -> dict:
    """value 0→1 を時間 0→1 で結ぶ 2 キーのカーブ。slope0=始点傾き / slope1=終点傾き。"""
    return {
        "serializedVersion": "2",
        "m_Curve": [
            {"serializedVersion": "3", "time": 0.0, "value": 0.0,
             "inSlope": slope0, "outSlope": slope0, "tangentMode": 0, "weightedMode": 0,
             "inWeight": 0.0, "outWeight": 0.0},
            {"serializedVersion": "3", "time": 1.0, "value": 1.0,
             "inSlope": slope1, "outSlope": slope1, "tangentMode": 0, "weightedMode": 0,
             "inWeight": 0.0, "outWeight": 0.0},
        ],
        "m_PreInfinity": 2,
        "m_PostInfinity": 2,
        "m_RotationOrder": 0,
    }


# ── 共通カーブ（AngleMotionBuilder / BeatActionBuilder と同一定義） ─────────────
_DEFAULT_CURVE = {
    "serializedVersion": "2",
    "m_Curve": [
        {"serializedVersion": "3", "time": 0.0, "value": 0.0,
         "inSlope": 0.0, "outSlope": 0.0, "tangentMode": 0, "weightedMode": 0,
         "inWeight": 0.0, "outWeight": 0.0},
        {"serializedVersion": "3", "time": 1.0, "value": 1.0,
         "inSlope": 1.6216527223587037, "outSlope": 1.6216527223587037,
         "tangentMode": 0, "weightedMode": 0,
         "inWeight": 0.06108373403549194, "outWeight": 0.0},
    ],
    "m_PreInfinity": 2,
    "m_PostInfinity": 2,
    "m_RotationOrder": 0,
}

# ロールのスイープ：前半は中間へ加速、後半は端へ減速（中央最速・両端ゆっくり）
EASE_IN_CURVE = _make_curve(0.0, 2.0)
EASE_OUT_CURVE = _make_curve(2.0, 0.0)

_EPS = 1e-6


def _angle_value(motion_id: str, part: str, rx: float, ry: float, rz: float,
                 rotate_ms: int, curve: dict) -> dict:
    """playthisanglemotion の value。"""
    return {
        "id": motion_id,
        "priority": 0.0,
        "motionPartName": part,
        "gazeTracking": True,
        "isGesture": False,
        "permitEmotionalRollChange": True,
        "autoBeat": False,
        "autoBeatAfterMotion": 0,
        "relaxingEndEfforctor": False,
        "noneDirection": False,
        "angleData": [
            {
                "id": "motion",
                "targetRotation": {"x": rx, "y": ry, "z": rz},
                "stiffness": {"x": -1.0, "y": -1.0, "z": -1.0},
                "rotateTime": rotate_ms,
                "rotateCurve": curve,
                "keepTime": 0.0,
                "keepUntilNewElementAddtion": True,
                "targetRotationOffset": {"x": 0.0, "y": 0.0, "z": 0.0},
            }
        ],
    }


def _axes_to_rotation(axis: str, value: float,
                       axis2: str | None = None, value2: float = 0.0) -> tuple[float, float, float]:
    """axis/value（と任意の axis2/value2）を targetRotation の rx,ry,rz に変換する。"""
    rot = {"x": 0.0, "y": 0.0, "z": 0.0}
    for a, v in ((axis, value), (axis2, value2)):
        if a is None:
            continue
        if a not in rot:
            raise ValueError(f"unknown axis: {a!r}")
        rot[a] = v
    return rot["x"], rot["y"], rot["z"]


# ── raw 送信（socket を毎回渡す。単発用） ───────────────────────────────────────
def send_angle(s: socket.socket, motion_id: str, part: str, target_deg: float,
               rotate_ms: int, curve: dict = _DEFAULT_CURVE, axis: str = "x",
               target_deg2: float | None = None, axis2: str | None = None) -> None:
    """1 関節を指定軸 target_deg[deg] へ rotate_ms[ms] で動かす（腕・頭・体すべて共通）。
    axis="x"|"y"|"z"（既定 x）。axis2/target_deg2 を指定すると 2 軸目も同時にセットする
    （id=part の置換で 2 軸目が 0 に上書きされるのを防ぐ）。"""
    rx, ry, rz = _axes_to_rotation(axis, target_deg, axis2,
                                    target_deg2 if target_deg2 is not None else 0.0)
    line = f"playthisanglemotion={json.dumps(_angle_value(motion_id, part, rx, ry, rz, rotate_ms, curve), separators=(',', ':'))}\n"
    with _send_lock:
        s.sendall(line.encode("utf-8"))


def send_rollpose(s: socket.socket, degree: float, direction: str, speed: float | None = None) -> None:
    """体リーン（rollpose）。degree=リーン角 / direction="left"|"right" / speed=deg/sec。"""
    v: dict = {"degree": degree, "direction": direction, "samedirection": True}
    if speed is not None:
        v["rollspeed"] = speed
    line = f"rollpose={json.dumps(v, separators=(',', ':'))}\n"
    with _send_lock:
        s.sendall(line.encode("utf-8"))


def send_saccade(s: socket.socket, enabled: bool) -> None:
    """サッケード（自動の細かい視線移動）の有効/無効を切り替える。"""
    line = f"saccade={'true' if enabled else 'false'}\n"
    with _send_lock:
        s.sendall(line.encode("utf-8"))


def send_playmotion(s: socket.socket, *motion_ids: str) -> None:
    """ベース姿勢の再生（playmotion）。例: right_external / left_external。
    playthisanglemotion はこの base の上に相対加算されるので、起動時に base を確立する。"""
    line = "playmotion=" + ";".join(motion_ids) + ";\n"
    with _send_lock:
        s.sendall(line.encode("utf-8"))


# ── 向き制御（Body/Head/Eye controller） ────────────────────────────────────────
BODY_DEF_Y = 1.0             # Body controller の高さ [m]
GAZE_DEF_Y = 1.6             # Head/Eye controller の高さ（角度0°のとき）[m]
GAZE_Y_SIDE = 1.2            # Head/Eye controller の高さ（角度 GAZE_ANGLE_SIDE のとき）[m]
GAZE_ANGLE_SIDE = 60.0       # 高さが GAZE_Y_SIDE になる基準角度（= eyeのside角度）[deg]
ROT_RADIUS = 1.5             # xz 平面での回転半径 [m]（= 既定 z）
ORIENT_ANGULAR_SPEED = 45.0  # 向き変更の角速度 [deg/sec]


def gaze_y_for_deg(deg: float) -> float:
    """Head/EyeController の向き角度[deg]から、対応する高さyを線形補間で求める。
    角度0° -> GAZE_DEF_Y、角度 GAZE_ANGLE_SIDE -> GAZE_Y_SIDE、その間は線形。"""
    t = abs(deg) / GAZE_ANGLE_SIDE
    return GAZE_DEF_Y + t * (GAZE_Y_SIDE - GAZE_DEF_Y)


def _rotate_xz(x: float, y: float, z: float, angle_deg: float) -> tuple[float, float, float]:
    """点 (x,y,z) の xz 成分を y 軸まわりに angle_deg 回転する（y は不変。0°=正面、正=右）。"""
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    return x * c + z * s, y, -x * s + z * c


def _controller_value(controller_id: str, x: float, y: float, z: float, angular_speed: float) -> dict:
    """BodyController/HeadController/EyeController の value（ワールド座標の targetPoint へ向ける）。"""
    return {
        "id": controller_id,
        "motionTowardObject": "",
        "targetMotionMode": 2,   # ON_OBJECT（ワールド軸オフセット）
        "targetPoint": {"x": x, "y": y, "z": z},
        "translateAngularSpeed": angular_speed,
        "tracking": False,
        "mode": 1,               # SLERP
        "priority": 0,
    }


def send_controller(s: socket.socket, controller_id: str, x: float, y: float, z: float,
                     angular_speed: float = ORIENT_ANGULAR_SPEED) -> None:
    """向き制御コマンドを送信する。controller_id は "BodyController"|"HeadController"|"EyeController"。"""
    line = f"{controller_id}={json.dumps(_controller_value(controller_id, x, y, z, angular_speed), separators=(',', ':'))}\n"
    with _send_lock:
        s.sendall(line.encode("utf-8"))


# ── Sender（socket と現在角を 1 回保持。posture はこれを使う） ──────────────────
class Sender:
    """socket を握り、送信パーツを socket 引数なしで呼べるようにする。
    各関節の現在角（最後に指令した角度）を保持し、ビートの遷移判定に使う。
    状態共有のため、呼び出し側で 1 個だけ作って全 posture に渡すこと。"""

    def __init__(self, s: socket.socket) -> None:
        self._s = s
        self._cur: dict[str, float] = {}   # part -> 最後に指令した角度

    # ── 最小プリミティブ（id=part で送信し、現在角を記録） ───────────────────
    def angle(self, part: str, target_deg: float, ms: int, curve: dict = _DEFAULT_CURVE,
              axis: str = "x", target_deg2: float | None = None, axis2: str | None = None) -> None:
        send_angle(self._s, part, part, target_deg, ms, curve, axis,
                   target_deg2, axis2)   # motion id = part
        self._cur[part] = target_deg

    def rollpose(self, degree: float, direction: str, speed: float | None = None) -> None:
        send_rollpose(self._s, degree, direction, speed)

    def saccade(self, enabled: bool) -> None:
        send_saccade(self._s, enabled)

    def current(self, part: str, default: float = 0.0) -> float:
        return self._cur.get(part, default)

    # ── ビート（beat = 現在 → peak → 目標） ─────────────────────────────────
    def beat_up(self, joints, height: float, ms: int) -> None:
        """up: beat 関節は peak へ overshoot。遷移関節は中間まで（EASE_IN）。
        2 軸目（axis2）があれば、beat_delta2 を height でスケールして同時に送る。"""
        for j in joints:
            t2 = j.angle2 + j.beat_delta2 * height if j.axis2 is not None else None
            if j.beat_delta:
                self.angle(j.part, j.angle + j.beat_delta * height, ms, axis=j.axis,
                           target_deg2=t2, axis2=j.axis2)
            else:
                cur = self._cur.get(j.part, j.angle)
                if abs(cur - j.angle) > _EPS:          # まだ目標に居ない＝遷移関節
                    half = cur + (j.angle - cur) / 2.0
                    self.angle(j.part, half, ms, EASE_IN_CURVE, axis=j.axis,
                               target_deg2=t2, axis2=j.axis2)
                # 既に目標角なら up では何もしない

    def beat_down(self, joints, ms: int) -> None:
        """down: beat 関節は resting(angle) へ戻す。遷移関節は目標(angle)へ到達（EASE_OUT）。
        2 軸目（axis2）があれば resting(angle2) を同時に送る。"""
        for j in joints:
            t2 = j.angle2 if j.axis2 is not None else None
            if j.beat_delta:
                self.angle(j.part, j.angle, ms, axis=j.axis, target_deg2=t2, axis2=j.axis2)
            else:
                if abs(self._cur.get(j.part, j.angle) - j.angle) > _EPS:
                    self.angle(j.part, j.angle, ms, EASE_OUT_CURVE, axis=j.axis,
                               target_deg2=t2, axis2=j.axis2)

    # ── 胴体（頷き）。id=part で置換 ────────────────────────────────────────
    def body_forward(self, parts, ms: int) -> None:
        for part, deg in parts:
            self.angle(part, deg, ms)

    def body_reset(self, parts, ms: int) -> None:
        for part, _ in parts:
            self.angle(part, 0.0, ms)
        self.emotion(1.0, ms)
        threading.Timer((ms + 300) / 1000.0, self.emotion, args=(0.0, ms)).start()

    # ── arousal ──────────────────────────────────────────────────────────────
    def emotion(self, value: float, duration_ms: int) -> None:
        payload = json.dumps(
            {"dimension": "arousal", "value": value, "transitionDuration": duration_ms},
            separators=(",", ":"),
        )
        line = f"emotion={payload}\n"
        with _send_lock:
            self._s.sendall(line.encode("utf-8"))

    # ── 体リーン（rollpose） ────────────────────────────────────────────────
    def lean_to(self, direction: str, degree: float, ms: int) -> None:
        speed = degree / (ms / 1000.0) if ms > 0 else None
        self.rollpose(degree, direction, speed)

    def lean_reset(self, direction: str, degree: float, ms: int) -> None:
        speed = degree / (ms / 1000.0) if ms > 0 else None
        self.rollpose(0.0, direction, speed)

    # ── 向き（Body/Head/Eye controller） ────────────────────────────────────
    def orient(self, body_deg: float, head_deg: float, eye_deg: float, *,
               gaze_y: float = GAZE_DEF_Y, body_y: float = BODY_DEF_Y,
               radius: float = ROT_RADIUS, ms: int = 600,
               speed_deg: tuple[float, float, float] | None = None) -> None:
        """Body/Head/Eye をそれぞれ angle_deg（0°=正面, 正=右）へ向ける。
        speed = |speed_deg| / (ms/1000) で算出し、pose（playthisanglemotion）の
        移動時間と揃える。speed_deg 省略時は (body_deg, head_deg, eye_deg) を使う
        （= front からその角度へ向かう想定の移動量）。"""
        if speed_deg is None:
            speed_deg = (body_deg, head_deg, eye_deg)
        sec = ms / 1000.0
        b_spd, h_spd, e_spd = (
            abs(d) / sec if sec > 0 else ORIENT_ANGULAR_SPEED for d in speed_deg
        )
        bx, by, bz = _rotate_xz(0.0, body_y, radius, body_deg)
        hx, hy, hz = _rotate_xz(0.0, gaze_y, radius, head_deg)
        ex, ey, ez = _rotate_xz(0.0, gaze_y, radius, eye_deg)
        send_controller(self._s, "BodyController", bx, by, bz, b_spd)
        send_controller(self._s, "HeadController", hx, hy, hz, h_spd)
        send_controller(self._s, "EyeController", ex, ey, ez, e_spd)

    def orient_one(self, controller_id: str, deg: float, *,
                    y: float = GAZE_DEF_Y, radius: float = ROT_RADIUS,
                    ms: int = 600, speed_deg: float | None = None) -> None:
        """BodyController / HeadController / EyeController のいずれか1つだけを向ける。"""
        speed_deg = speed_deg if speed_deg is not None else deg
        sec = ms / 1000.0
        spd = abs(speed_deg) / sec if sec > 0 else ORIENT_ANGULAR_SPEED
        x, y_, z = _rotate_xz(0.0, y, radius, deg)
        send_controller(self._s, controller_id, x, y_, z, spd)
