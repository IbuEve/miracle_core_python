"""
MiracleHuman Command Builder
コマンドを構築する純粋な値オブジェクト群。
送信はTCPClient (MiracleAsyncClient) 側で行う。

Usage:
    cmd = MiracleCommands.eye_controller(x=0.0, y=1.2, z=1.0)
    await client.send_json_command(cmd.key, cmd.value)
    # or
    await client.send_command(cmd.key, cmd.value)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Union


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class TargetMotionMode(IntEnum):
    FROM_OBJECT = 0  # motionTowardObject のローカル軸でオフセット
    FROM_ROBOT = 1  # ロボット体幹軸でオフセット（定型動作向け）
    ON_OBJECT = 2  # ワールド軸でオフセット（最頻用）


class InterpolationMode(IntEnum):
    LERP = 0
    SLERP = 1  # default


# ------------------------------------------------------------------
# Value object
# ------------------------------------------------------------------

@dataclass(frozen=True)
class MiracleCommand:
    """
    MiracleHuman への送信コマンドを表す純粋な値オブジェクト。

    key   : コマンド名（例: "EyeController", "arousal"）
    value : 文字列コマンドの場合は str、JSONコマンドの場合は dict

    TCPClient での送信例:
        if isinstance(cmd.value, dict):
            await client.send_json_command(cmd.key, cmd.value)
        else:
            await client.send_command(cmd.key, cmd.value)
    """

    key: str
    value: Union[str, dict]


# ------------------------------------------------------------------
# Command builder
# ------------------------------------------------------------------

class MiracleCommands:
    """
    MiracleHuman コマンドのファクトリクラス。
    すべてのメソッドは MiracleCommand を返す静的メソッド。
    """

    # ----------------------------------------------------------------
    # モーションコントローラ
    # ----------------------------------------------------------------

    @staticmethod
    def eye_controller(
        x: float,
        y: float,
        z: float,
        *,
        motion_toward_object: str = "",
        target_motion_mode: TargetMotionMode = TargetMotionMode.ON_OBJECT,
        angular_speed: float = 90.0,
        tracking: bool = False,
        priority: float = 0,
        mode: InterpolationMode = InterpolationMode.SLERP,
    ) -> MiracleCommand:
        """視線制御。priority >= 2 で瞬きが連動する。"""
        return MiracleCommand(
            "EyeController",
            {
                "id": "EyeController",
                "motionTowardObject": motion_toward_object,
                "targetMotionMode": int(target_motion_mode),
                "targetPoint": {"x": x, "y": y, "z": z},
                "translateAngularSpeed": angular_speed,
                "tracking": tracking,
                "mode": int(mode),
                "priority": priority,
            },
        )

    @staticmethod
    def head_controller(
        x: float,
        y: float,
        z: float,
        *,
        motion_toward_object: str = "",
        target_motion_mode: TargetMotionMode = TargetMotionMode.ON_OBJECT,
        angular_speed: float = 90.0,
        tracking: bool = False,
        priority: float = 0,
        mode: InterpolationMode = InterpolationMode.SLERP,
    ) -> MiracleCommand:
        """頭部制御。"""
        return MiracleCommand(
            "HeadController",
            {
                "id": "HeadController",
                "motionTowardObject": motion_toward_object,
                "targetMotionMode": int(target_motion_mode),
                "targetPoint": {"x": x, "y": y, "z": z},
                "translateAngularSpeed": angular_speed,
                "tracking": tracking,
                "mode": int(mode),
                "priority": priority,
            },
        )

    @staticmethod
    def body_controller(
        x: float,
        y: float,
        z: float,
        *,
        motion_toward_object: str = "",
        target_motion_mode: TargetMotionMode = TargetMotionMode.ON_OBJECT,
        angular_speed: float = 90.0,
        tracking: bool = False,
        priority: float = 0,
        mode: InterpolationMode = InterpolationMode.SLERP,
    ) -> MiracleCommand:
        """体幹制御。"""
        return MiracleCommand(
            "BodyController",
            {
                "id": "BodyController",
                "motionTowardObject": motion_toward_object,
                "targetMotionMode": int(target_motion_mode),
                "targetPoint": {"x": x, "y": y, "z": z},
                "translateAngularSpeed": angular_speed,
                "tracking": tracking,
                "mode": int(mode),
                "priority": priority,
            },
        )

    @staticmethod
    def right_hand_controller(
        x: float,
        y: float,
        z: float,
        *,
        motion_toward_object: str = "",
        target_motion_mode: TargetMotionMode = TargetMotionMode.ON_OBJECT,
        translate_speed: float = 1.0,
        translate_time: int = -1,
        angular_speed: float = -1,
        tracking: bool = False,
        priority: float = 0,
        mode: InterpolationMode = InterpolationMode.SLERP,
    ) -> MiracleCommand:
        """右手制御。手先の移動には translate_speed が適切。"""
        return MiracleCommand(
            "RightHandController",
            {
                "id": "RightHandController",
                "motionTowardObject": motion_toward_object,
                "targetMotionMode": int(target_motion_mode),
                "targetPoint": {"x": x, "y": y, "z": z},
                "translateSpeed": translate_speed,
                "translateTime": translate_time,
                "translateAngularSpeed": angular_speed,
                "tracking": tracking,
                "mode": int(mode),
                "priority": priority,
            },
        )

    @staticmethod
    def left_hand_controller(
        x: float,
        y: float,
        z: float,
        *,
        motion_toward_object: str = "",
        target_motion_mode: TargetMotionMode = TargetMotionMode.ON_OBJECT,
        translate_speed: float = 1.0,
        translate_time: int = -1,
        angular_speed: float = -1,
        tracking: bool = False,
        priority: float = 0,
        mode: InterpolationMode = InterpolationMode.SLERP,
    ) -> MiracleCommand:
        """左手制御。"""
        return MiracleCommand(
            "LeftHandController",
            {
                "id": "LeftHandController",
                "motionTowardObject": motion_toward_object,
                "targetMotionMode": int(target_motion_mode),
                "targetPoint": {"x": x, "y": y, "z": z},
                "translateSpeed": translate_speed,
                "translateTime": translate_time,
                "translateAngularSpeed": angular_speed,
                "tracking": tracking,
                "mode": int(mode),
                "priority": priority,
            },
        )

    # ----------------------------------------------------------------
    # アトラクティブネス
    # ----------------------------------------------------------------

    @staticmethod
    def attractiveness(
        part: str,
        value: float,
        *,
        transition_duration: int = -1,
        transition_speed: float = -1.0,
    ) -> MiracleCommand:
        """
        顔・体の向く度合い制御。
        part: "Head" / "Body" / "Stance"
        value: -1.0（対象からそらす）~ +1.0（対象に向ける）
        transition_duration: 変化時間 [msec]（-1 で即時）
        transition_speed: 変化速度 [/sec]（-1 でデフォルト）
        """
        payload: dict = {"partName": part, "attractiveness": value}
        if transition_duration >= 0:
            payload["transitionDuration"] = transition_duration
        if transition_speed >= 0:
            payload["transitionSpeed"] = transition_speed
        return MiracleCommand("attractiveness", payload)

    # ----------------------------------------------------------------
    # 視線系スペシャルコマンド
    # ----------------------------------------------------------------

    @staticmethod
    def gaze_avert(
        pitch_degree: float = 0.0,
        yaw_degree: float = 0.0,
        angular_speed: float = 180.0,
    ) -> MiracleCommand:
        """視線を意図的にそらす。pitch > 0 で下方向。"""
        return MiracleCommand(
            "gazeavert",
            {
                "pitch_degree": pitch_degree,
                "yaw_degree": yaw_degree,
                "angularSpeed": angular_speed,
            },
        )

    @staticmethod
    def saccade(enabled: bool) -> MiracleCommand:
        """サッケードの自動実行を ON/OFF する。"""
        return MiracleCommand("saccade", str(enabled).lower())

    # ----------------------------------------------------------------
    # ジェスチャ再生
    # ----------------------------------------------------------------

    @staticmethod
    def play_motion(motion_ids: list[tuple[str, float]] | list[str]) -> MiracleCommand:
        """
        定義済みジェスチャを再生する。
        motion_ids: モーションIDのリスト、またはID+速度スケールのタプルリスト
        例: ["greeting"]  /  [("greeting", 1.5), ("right_hand_byebye", 0.5)]
        """
        parts = []
        for item in motion_ids:
            if isinstance(item, tuple):
                parts.append(f"{item[0]}/{item[1]}")
            else:
                parts.append(item)
        return MiracleCommand("playmotion", ";".join(parts) + ";")

    @staticmethod
    def reset_all_motions() -> MiracleCommand:
        """再生中のモーションをすべて停止する。"""
        return MiracleCommand("reset", "all_playing_motions")

    @staticmethod
    def play_action(action_id: str) -> MiracleCommand:
        """定義済みアクションを名前で再生する。"""
        return MiracleCommand("playaction", action_id)

    @staticmethod
    def play_this_action(
        action_id: str,
        action_id_list: list[dict],
        *,
        destroy_after_finish: bool = True,
    ) -> MiracleCommand:
        """
        アクションをインラインで定義して再生する。

        action_id_list の各要素は以下の構造を持つ dict:
            {
                "action": {
                    "actionType": "motion" / "facial" / "attractiveness" / "controller",
                    "predefinedActionName": str,   # motion / facial 用
                    "thisCmd": str,                # controller 用（JSON文字列）
                    "attractiveProp": dict,        # attractiveness 用
                },
                "startdelay": int,
                "speedScale": float,    # optional
                "intensity": float,     # optional
                "nextActions": [...]    # 同構造のリスト（再帰）
            }

        例:
            MiracleCommands.play_this_action(
                "actiontest2",
                [{
                    "action": {"actionType": "motion", "predefinedActionName": "greeting"},
                    "startdelay": 0,
                    "speedScale": 1.0,
                    "nextActions": [],
                }],
            )
        """
        return MiracleCommand(
            "playthisaction",
            {
                "id": action_id,
                "destoryAfterFinish": destroy_after_finish,
                "actionIDList": action_id_list,
            },
        )

    # ----------------------------------------------------------------
    # 内部状態（感情）
    # ----------------------------------------------------------------

    @staticmethod
    def arousal(value: float) -> MiracleCommand:
        """覚醒度を即時設定する。"""
        return MiracleCommand("arousal", str(value))

    @staticmethod
    def valence(value: float) -> MiracleCommand:
        """感情の正負を即時設定する。"""
        return MiracleCommand("valence", str(value))

    @staticmethod
    def dominance(value: float) -> MiracleCommand:
        """優位性を即時設定する。"""
        return MiracleCommand("dominance", str(value))

    @staticmethod
    def emotion(
        dimension: str,
        value: float,
        *,
        transition_duration: int = -1,
        transition_speed: float = -1.0,
    ) -> MiracleCommand:
        """
        感情を時間・速度指定で変化させる。
        dimension: "arousal" / "valence" / "dominance"
        transition_duration と transition_speed はどちらか一方を指定する。
        """
        payload: dict = {"dimension": dimension, "value": value}
        if transition_duration >= 0:
            payload["transitionDuration"] = transition_duration
        if transition_speed >= 0:
            payload["transitionSpeed"] = transition_speed
        return MiracleCommand("emotion", payload)

    # ----------------------------------------------------------------
    # 表情
    # ----------------------------------------------------------------

    @staticmethod
    def set_face(
        face_id: str,
        *,
        speed_scale: float = 1.0,
        intensity: float = 1.0,
        user_specify_id: int | None = None,
    ) -> MiracleCommand:
        """
        定義済み表情を再生する。
        speed_scale: 0.001（遅い）~ 10.0（早い）
        intensity:   0.001（小さい）~ 1.0（大きい）
        """
        payload: dict = {
            "id": face_id,
            "speedScale": speed_scale,
            "intensity": intensity,
        }
        if user_specify_id is not None:
            payload["userSpecifyId"] = user_specify_id
        return MiracleCommand("setface", payload)

    @staticmethod
    def set_manual_facs(
        facs_name: str,
        value: float,
        duration: int,
    ) -> MiracleCommand:
        """
        FACSパラメータを手動指定する。
        facs_name: "MouthOpenClose", "UpperLip" など
        value: -1.0 ~ +1.0
        duration: > 0 [msec] / <= 0 でそのActionUnitを無効化
        """
        return MiracleCommand(
            "setmanualfacs",
            {
                "facsname": facs_name,
                "value": value,
                "duration": duration,
            },
        )

    @staticmethod
    def blink(duration: int, *, intentional: bool = True) -> MiracleCommand:
        """
        任意のタイミングで瞬きをトリガーする。
        intentional=True で抑制されず上下瞬きになる。
        """
        return MiracleCommand("blink", {"duration": duration, "intentional": intentional})

    @staticmethod
    def blink_module(enabled: bool) -> MiracleCommand:
        """瞬きモジュールの ON/OFF。"""
        return MiracleCommand("blinkmodule", {"enable": enabled})

    # ----------------------------------------------------------------
    # Listening Behavior
    # ----------------------------------------------------------------

    @staticmethod
    def listening_module(enabled: bool) -> MiracleCommand:
        """対話相手のセンシングに合わせた頷き自動生成の ON/OFF。"""
        return MiracleCommand("listeningmodule", {"enable": enabled})

    # ----------------------------------------------------------------
    # ターゲット設定
    # ----------------------------------------------------------------

    @staticmethod
    def target_human(unique_id: int) -> MiracleCommand:
        """メインターゲットを unique ID で指定する。"""
        return MiracleCommand("targethuman", str(unique_id))

    @staticmethod
    def sub_target_human(unique_id: int) -> MiracleCommand:
        """サブターゲットを unique ID で指定する。"""
        return MiracleCommand("subtargethuman", str(unique_id))

    @staticmethod
    def main_target_name(name: str) -> MiracleCommand:
        """
        人またはロボットをターゲットに指定する。
        人: "unique:4"  /  ロボット: "N1H.test"
        """
        return MiracleCommand("maintargetname", name)

    @staticmethod
    def sub_target_name(name: str) -> MiracleCommand:
        """サブターゲットを名前で指定する。"""
        return MiracleCommand("subtargetname", name)

    # ----------------------------------------------------------------
    # 体幹・姿勢
    # ----------------------------------------------------------------

    @staticmethod
    def roll_pose(
        degree: float,
        direction: str,
        *,
        same_direction: bool = True,
        roll_speed: float | None = None,
    ) -> MiracleCommand:
        """
        ロール姿勢を手動制御する（Emotion2Pose が自動停止）。
        direction: "left" / "right"
        """
        payload: dict = {
            "degree": degree,
            "direction": direction,
            "samedirection": same_direction,
        }
        if roll_speed is not None:
            payload["rollspeed"] = roll_speed
        return MiracleCommand("rollpose", payload)

    @staticmethod
    def module_control(module_name: str, permit: bool) -> MiracleCommand:
        """
        モジュールの ON/OFF を制御する。
        例: module_name="Emotion2Pose"
        """
        return MiracleCommand("modulecontrol", {"moduleName": module_name, "permit": permit})

    @staticmethod
    def cpg(
        scale: float = 2.5,
        frequency: float = 0.15,
        perlin_scale: float = 1.0,
    ) -> MiracleCommand:
        """
        Central Pattern Generator（体の揺らぎ）の設定。
        scale: 0.0（小）~ 2.5（デフォルト）~ 5.0（大）
        frequency: 0.0（遅）~ 0.15（デフォルト）~ 0.3（速）
        """
        return MiracleCommand(
            "cpg",
            {
                "scale": scale,
                "frequency": frequency,
                "perlinscale": perlin_scale,
            },
        )

    # ----------------------------------------------------------------
    # 仮想オブジェクト
    # ----------------------------------------------------------------

    @staticmethod
    def create_object(
        obj_id: str,
        position: tuple[float, float, float],
        scale: tuple[float, float, float],
        *,
        rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
        color: tuple[int, int, int, int] = (0, 5, 250, 128),
        is_look_target: bool = True,
        is_pointing_target: bool = False,
    ) -> MiracleCommand:
        """仮想オブジェクト（Cube）を生成する。位置・回転はワールド座標。"""
        px, py, pz = position
        sx, sy, sz = scale
        rx, ry, rz = rotation
        r, g, b, a = color
        return MiracleCommand(
            "createobject",
            {
                "id": obj_id,
                "scale": {"x": sx, "y": sy, "z": sz},
                "position": {"x": px, "y": py, "z": pz},
                "rotation": {"x": rx, "y": ry, "z": rz},
                "color": {"r": r, "g": g, "b": b, "a": a},
                "isLookTarget": is_look_target,
                "isPointingTarget": is_pointing_target,
            },
        )

    @staticmethod
    def move_object(
        obj_id: str,
        target_point: tuple[float, float, float],
        *,
        target_rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
        translate_time: int = 1000,
        translate_speed: float = -1.0,
        rotate_time: int = -1,
        rotate_speed: float = -1.0,
        keep_time: int = 0,
        mode: InterpolationMode = InterpolationMode.SLERP,
    ) -> MiracleCommand:
        """playthismotionで仮想オブジェクトを移動させる。"""
        x, y, z = target_point
        rx, ry, rz = target_rotation
        return MiracleCommand(
            "playthismotion",
            {
                "id": f"{obj_id}_move",
                "motionPartName": obj_id,
                "motionData": [
                    {
                        "id": "0",
                        "targetPoint": {"x": x, "y": y, "z": z},
                        "translateSpeed": translate_speed,
                        "translateTime": translate_time,
                        "targetRotation": {"x": rx, "y": ry, "z": rz},
                        "rotateSpeed": rotate_speed,
                        "rotateTime": rotate_time,
                        "keepTime": keep_time,
                        "mode": int(mode),
                    }
                ],
            },
        )

    @staticmethod
    def delete_object(obj_id: str) -> MiracleCommand:
        """仮想オブジェクトを削除する。"""
        return MiracleCommand("deleteobject", {"id": obj_id})

    @staticmethod
    def get_object(obj_id: str) -> MiracleCommand:
        """オブジェクト情報を取得する（レスポンスは gotobject=... で返る）。"""
        return MiracleCommand("getobject", obj_id)

    # ----------------------------------------------------------------
    # その他
    # ----------------------------------------------------------------

    @staticmethod
    def send_motor_cmd(enabled: bool) -> MiracleCommand:
        """モーターコマンド送信の ON/OFF。"""
        return MiracleCommand("sendmotorcmd", str(enabled).lower())
