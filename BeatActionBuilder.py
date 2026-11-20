"""
Beat Action Builder
ビートジェスチャ（上げ→下げ→戻し＋胴体前傾＋体リーン）を 1 つの playthisaction に
組み上げる純粋なコマンド製造クラス。

設計方針（主体性を持たない）:
  - 乱数・両手ミラー・クランプ・height→時間の換算・HandStack などの「判断」は一切しない。
    呼び出し側が具体値を解決してから渡す。本クラスは渡された数値をコマンドに組むだけ。
  - 送信もしない。MiracleCommand（key="playthisaction", value=dict）を返すだけ。
    送信は TCPClient / 呼び出し側が行う。
  - sleep もスレッドも持たない。3 フェーズの時間関係は playthisaction の
    startdelay（アクション開始からの絶対 ms）で表現する＝サーバ側にタイミングを委ねる。

フェーズ構成（フラット: 各ノードを startdelay でずらして並べる）:
  ① 上げ  startdelay=0
       arm_joints を peak×height へ / rolls を half へ(EASE_IN)
  ② 下げ  startdelay=up_ms+hold_ms
       arm_joints を 0 へ / rolls を to へ(EASE_OUT) / body_parts 前傾 / rollpose リーン
  ③ 戻し  startdelay=up_ms+hold_ms+down_ms
       body_parts→0 / rollpose→0
  （roll は②で目標へ到達したまま保持＝差し出し位置。arm は②で基準へ戻る。）

Usage:
    cmd = BeatActionCommands.beat(
        "beat0",
        arm_joints=[ArmJoint("RightArm_Forward_Joint", 10.0), ...],
        beat_ms=300,
        height=0.8,
        rolls=[RollMove("RightArm_Roll_Joint", half_deg=10.0, to_deg=20.0)],
        body_parts=[BodyTilt("head_x", "Head_Joint", 10.0)],
        lean_degree=5.0, lean_direction="right",
    )
    # cmd.value は playthisaction の dict
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .CommandBuilder import MiracleCommand

# ── action に各コマンドを埋め込むときの actionType ──────────────────────────────────
ANGLE_ACTION_TYPE = "thisanglemotion"   # playthisanglemotion を埋める
ROLLPOSE_ACTION_TYPE = "rollpose"       # rollpose を埋める


# ── カーブ（AngleMotionBuilder / keyboad_double と同一定義） ──────────────────────────
def _make_curve(slope0: float, slope1: float) -> dict:
    """value 0→1 を時間 0→1 で結ぶ 2 キーのカーブ。slope0=始点傾き / slope1=終点傾き。"""
    return {
        "serializedVersion": "2",
        "m_Curve": [
            {
                "serializedVersion": "3",
                "time": 0.0, "value": 0.0,
                "inSlope": slope0, "outSlope": slope0,
                "tangentMode": 0, "weightedMode": 0,
                "inWeight": 0.0, "outWeight": 0.0,
            },
            {
                "serializedVersion": "3",
                "time": 1.0, "value": 1.0,
                "inSlope": slope1, "outSlope": slope1,
                "tangentMode": 0, "weightedMode": 0,
                "inWeight": 0.0, "outWeight": 0.0,
            },
        ],
        "m_PreInfinity": 2,
        "m_PostInfinity": 2,
        "m_RotationOrder": 0,
    }


DEFAULT_CURVE = {
    "serializedVersion": "2",
    "m_Curve": [
        {
            "serializedVersion": "3",
            "time": 0.0, "value": 0.0,
            "inSlope": 0.0, "outSlope": 0.0,
            "tangentMode": 0, "weightedMode": 0,
            "inWeight": 0.0, "outWeight": 0.0,
        },
        {
            "serializedVersion": "3",
            "time": 1.0, "value": 1.0,
            "inSlope": 1.6216527223587037, "outSlope": 1.6216527223587037,
            "tangentMode": 0, "weightedMode": 0,
            "inWeight": 0.06108373403549194, "outWeight": 0.0,
        },
    ],
    "m_PreInfinity": 2,
    "m_PostInfinity": 2,
    "m_RotationOrder": 0,
}

# ロールのスイープ：前半は中間点へ加速、後半は端へ減速（中央最速・両端ゆっくり）
EASE_IN_CURVE = _make_curve(0.0, 2.0)
EASE_OUT_CURVE = _make_curve(2.0, 0.0)


# ── 入力データ（すべて呼び出し側が解決済みの具体値で渡す） ─────────────────────────
@dataclass(frozen=True)
class ArmJoint:
    """上下動する腕関節。実角 = peak_deg × height。左右ミラーは呼び出し側で適用済み。"""
    part: str
    peak_deg: float


@dataclass(frozen=True)
class RollMove:
    """out のロール遷移。上げで half_deg(EASE_IN)→下げで to_deg(EASE_OUT)。絶対角[deg]。"""
    part: str
    half_deg: float
    to_deg: float


@dataclass(frozen=True)
class BodyTilt:
    """下げフェーズの胴体前傾（戻しで 0 に戻す）。deg は x 角度[deg]。"""
    motion_id: str
    part: str
    deg: float


# ── 内部ビルダー ────────────────────────────────────────────────────────────────
def _angle_motion_value(
    motion_id: str, motion_part: str, rx: float,
    rotate_time: int, curve: dict, *, keep_time: float = 0.0, priority: float = 0.0,
) -> dict:
    """playthisanglemotion の value（x 軸のみ動かす）。"""
    return {
        "id": motion_id,
        "priority": priority,
        "motionPartName": motion_part,
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
                "targetRotation": {"x": rx, "y": 0.0, "z": 0.0},
                "stiffness": {"x": -1.0, "y": -1.0, "z": -1.0},
                "rotateTime": rotate_time,
                "rotateCurve": curve,
                "keepTime": keep_time,
                "keepUntilNewElementAddtion": True,
                "targetRotationOffset": {"x": 0.0, "y": 0.0, "z": 0.0},
            }
        ],
    }


def _rollpose_value(degree: float, direction: str, speed: float | None) -> dict:
    v: dict = {"degree": degree, "direction": direction, "samedirection": True}
    if speed is not None:
        v["rollspeed"] = speed
    return v


def _node(action_type: str, this_cmd_value: dict, startdelay: int) -> dict:
    """thisCmd に JSON 文字列を埋めた action ノード（フラット配置・子なし）。"""
    return {
        "action": {
            "actionType": action_type,
            "predefinedActionName": "",
            "thisCmd": json.dumps(this_cmd_value, separators=(",", ":")),
        },
        "startdelay": startdelay,
        "speedScale": 1.0,
        "intensity": 1.0,
        "nextActions": [],
    }


class BeatActionCommands:
    """ビート 1 発を 1 つの playthisaction にまとめるファクトリ。"""

    @staticmethod
    def beat(
        action_id: str,
        *,
        arm_joints: list[ArmJoint],
        beat_ms: int,
        up_ms: int | None = None,
        down_ms: int | None = None,
        return_ms: int | None = None,
        height: float = 1.0,
        hold_ms: int = 0,
        rolls: list[RollMove] | None = None,
        body_parts: list[BodyTilt] | None = None,
        lean_degree: float = 0.0,
        lean_direction: str = "right",
        lean_speed: float | None = None,
        priority: float = 0.0,
        destroy_after_finish: bool = True,
    ) -> MiracleCommand:
        """
        ビート 1 発の playthisaction を組む。

        arm_joints    : 上下動する関節（peak は実角、左右ミラー適用済み）。空なら胴体のみのビート。
        beat_ms       : 各フェーズの既定時間[ms]（呼び出し側が計算して渡す）。
        up_ms/down_ms/return_ms : 各フェーズ時間の個別上書き（未指定なら beat_ms）。
        height        : 上下動の振幅スケール（arm 実角 = peak × height）。
        hold_ms       : 上げ(peak)で静止保持する時間[ms]。0 で保持なし。
        rolls         : out のロール遷移（上げ half / 下げ to）。None で純ビート/in。
        body_parts    : 下げで前傾し戻しで 0 に戻す胴体部位。None で胴体なし。
        lean_degree   : 体リーン角。0 でリーンなし。
        lean_direction: "left" / "right"。
        lean_speed    : rollpose の速度[deg/sec]。None なら lean_degree/(down_ms/1000) を自動採用。
        """
        up = up_ms if up_ms is not None else beat_ms
        down = down_ms if down_ms is not None else beat_ms
        ret = return_ms if return_ms is not None else beat_ms

        t_down = up + hold_ms          # 下げ開始（アクション開始からの絶対 ms）
        t_return = t_down + down        # 戻し開始

        rolls = rolls or []
        body_parts = body_parts or []
        nodes: list[dict] = []

        # ① 上げ（startdelay=0）: 腕 peak×height / ロール half(EASE_IN)
        for j in arm_joints:
            nodes.append(_node(
                ANGLE_ACTION_TYPE,
                _angle_motion_value(
                    f"{action_id}_arm_{j.part}", j.part, j.peak_deg * height,
                    up, DEFAULT_CURVE, priority=priority,
                ),
                startdelay=0,
            ))
        for r in rolls:
            nodes.append(_node(
                ANGLE_ACTION_TYPE,
                _angle_motion_value(
                    f"{action_id}_roll_{r.part}", r.part, r.half_deg,
                    up, EASE_IN_CURVE, priority=priority,
                ),
                startdelay=0,
            ))

        # ② 下げ（startdelay=t_down）: 腕→0 / ロール to(EASE_OUT) / 胴体前傾 / リーン
        for j in arm_joints:
            nodes.append(_node(
                ANGLE_ACTION_TYPE,
                _angle_motion_value(
                    f"{action_id}_arm_{j.part}", j.part, 0.0,
                    down, DEFAULT_CURVE, priority=priority,
                ),
                startdelay=t_down,
            ))
        for r in rolls:
            nodes.append(_node(
                ANGLE_ACTION_TYPE,
                _angle_motion_value(
                    f"{action_id}_roll_{r.part}", r.part, r.to_deg,
                    down, EASE_OUT_CURVE, priority=priority,
                ),
                startdelay=t_down,
            ))
        for b in body_parts:
            nodes.append(_node(
                ANGLE_ACTION_TYPE,
                _angle_motion_value(
                    f"{action_id}_body_{b.part}", b.part, b.deg,
                    down, DEFAULT_CURVE, priority=priority,
                ),
                startdelay=t_down,
            ))
        if lean_degree != 0.0:
            speed = lean_speed if lean_speed is not None else (
                lean_degree / (down / 1000.0) if down > 0 else None
            )
            nodes.append(_node(
                ROLLPOSE_ACTION_TYPE,
                _rollpose_value(lean_degree, lean_direction, speed),
                startdelay=t_down,
            ))

        # ③ 戻し（startdelay=t_return）: 胴体→0 / リーン→0
        for b in body_parts:
            nodes.append(_node(
                ANGLE_ACTION_TYPE,
                _angle_motion_value(
                    f"{action_id}_body_{b.part}", b.part, 0.0,
                    ret, DEFAULT_CURVE, priority=priority,
                ),
                startdelay=t_return,
            ))
        if lean_degree != 0.0:
            speed = lean_speed if lean_speed is not None else (
                lean_degree / (ret / 1000.0) if ret > 0 else None
            )
            nodes.append(_node(
                ROLLPOSE_ACTION_TYPE,
                _rollpose_value(0.0, lean_direction, speed),
                startdelay=t_return,
            ))

        return MiracleCommand(
            "playthisaction",
            {
                "id": action_id,
                "destoryAfterFinish": destroy_after_finish,
                "actionIDList": nodes,
            },
        )
