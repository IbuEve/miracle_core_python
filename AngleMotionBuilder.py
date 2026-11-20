"""
AngleMotion Command Builder
playthisanglemotion コマンドを構築するファクトリクラス。

rotateTime を引数で渡すだけで速度を動的に変えられる。
送信は CommandBuilder.MiracleCommand / MiracleAsyncClient で行う。

Usage:
    cmd = AngleMotionCommands.right_wrist_beat_z_down(rotate_time=150)
    await client.send_command(cmd.key, cmd.value)
"""

from __future__ import annotations

from .CommandBuilder import MiracleCommand

# ── 部位名定数 ────────────────────────────────────────────────────────────────
_FOREARM      = "RightForeArm_Forward_Joint"
_WRIST        = "RightHand_Joint"
_UPPERARM     = "RightArm_Forward_Joint"
_ARM_ROLL     = "RightArm_Roll_Joint"        # ロール軸 x: -45(左) ~ +45(右)
_FOREARM_ROLL = "RightForeArm_Roll_Joint"    # 前腕ロール軸 x（掌向き切替: side=-60 / up=0）

_LEFT_FOREARM  = "LeftForeArm_Forward_Joint"
_LEFT_WRIST    = "LeftHand_Joint"
_LEFT_UPPERARM = "LeftArm_Forward_Joint"
_LEFT_ARM_ROLL = "LeftArm_Roll_Joint"   # ロール軸 x: -45(右) ~ +45(左)（右腕と逆）

# ── 共通カーブ（全JSONで同一） ─────────────────────────────────────────────────
_DEFAULT_CURVE = {
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


class AngleMotionCommands:
    """
    playthisanglemotion コマンドのファクトリクラス。

    全メソッドは MiracleCommand を返す。
    rotate_time [ms] を変えるだけで動作速度を動的に調整できる。
    """

    # ----------------------------------------------------------------
    # 汎用ビルダー
    # ----------------------------------------------------------------

    @staticmethod
    def play_this_angle_motion(
        motion_id: str,
        motion_part: str,
        rx: float,
        ry: float,
        rz: float,
        *,
        rotate_time: int = 250,
        keep_time: float = 0.0,
        priority: float = 0.0,
    ) -> MiracleCommand:
        """
        任意の部位・角度・速度でアングルモーションを生成する。

        motion_id   : Miracle 上の一意 ID（同 ID の重複送信は上書きになる）
        motion_part : 部位名（例: "RightHand_Joint"）
        rx/ry/rz    : 目標回転角度 [deg]
        rotate_time : 到達時間 [ms]（小さいほど速い）
        keep_time   : 終端姿勢の保持時間 [ms]
        """
        return MiracleCommand(
            "playthisanglemotion",
            {
                "id": motion_id,
                "priority": priority,
                "motionPartName": motion_part,
                "gazeTracking": True,
                "isGesture": False,
                "permitEmotionalRollChange": True,
                "autoBeat": False,
                "autoBeatAfterMotion": 0,
                "relaxingEndEfforctor": True,
                "noneDirection": False,
                "angleData": [
                    {
                        "id": "motion",
                        "targetRotation": {"x": rx, "y": ry, "z": rz},
                        "stiffness": {"x": -1.0, "y": -1.0, "z": -1.0},
                        "rotateTime": rotate_time,
                        "rotateCurve": _DEFAULT_CURVE,
                        "keepTime": keep_time,
                        "keepUntilNewElementAddtion": True,
                        "targetRotationOffset": {"x": 0.0, "y": 0.0, "z": 0.0},
                    }
                ],
            },
        )

    # ----------------------------------------------------------------
    # 前腕 (RightForeArm_Forward_Joint)
    # ----------------------------------------------------------------

    @staticmethod
    def right_arm_beat_up(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_arm_beat_up", _FOREARM, -15.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def right_arm_beat_down(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_arm_beat_down", _FOREARM, 0.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 手首 (RightHand_Joint)
    # ----------------------------------------------------------------

    @staticmethod
    def right_wrist_beat_z_up(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_wrist_beat_z_up", _WRIST, 0.0, 0.0, -20.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def right_wrist_beat_z_down(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_wrist_beat_z_down", _WRIST, 0.0, 0.0, 20.0,
            rotate_time=rotate_time,
        )


    @staticmethod
    def right_wrist_beat_x_up(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_wrist_beat_x_up", _WRIST, 20.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def right_wrist_beat_x_down(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_wrist_beat_x_down", _WRIST, -20.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 上腕ロール (RightArm_Roll_Joint)  x: -45(左) ~ +45(右)
    # ----------------------------------------------------------------

    @staticmethod
    def right_arm_roll(rx: float, *, rotate_time: int = 250) -> MiracleCommand:
        """ビート方向に応じて腕をロールする。rx の範囲は -45 ~ +45 [deg]。"""
        return AngleMotionCommands.play_this_angle_motion(
            "right_arm_roll", _ARM_ROLL, rx, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 前腕ロール (RightForeArm_Roll_Joint)  掌向き切替: side=-60 / up=0
    # ----------------------------------------------------------------

    @staticmethod
    def right_forearm_roll(rx: float, *, rotate_time: int = 250) -> MiracleCommand:
        """前腕をロールして掌の向きを切り替える。external の side(-60) / up(0) に使う。"""
        return AngleMotionCommands.play_this_angle_motion(
            "right_forearm_roll", _FOREARM_ROLL, rx, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 上腕 (RightArm_Forward_Joint)
    # ----------------------------------------------------------------

    @staticmethod
    def right_upper_beat_default(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_upper_beat_default", _UPPERARM, 0.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def right_upper_beat_pull(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_upper_beat_pull", _UPPERARM, -5.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def right_upper_beat_push(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_upper_beat_push", _UPPERARM, 5.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 左前腕 (LeftForeArm_Forward_Joint)
    # ----------------------------------------------------------------

    @staticmethod
    def left_arm_beat_up(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_arm_beat_up", _LEFT_FOREARM, 15.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def left_arm_beat_down(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_arm_beat_down", _LEFT_FOREARM, 0.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 左手首 (LeftHand_Joint)
    # ----------------------------------------------------------------

    @staticmethod
    def left_wrist_beat_x_up(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_wrist_beat_x_up", _LEFT_WRIST, 20.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def left_wrist_beat_x_down(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_wrist_beat_x_down", _LEFT_WRIST, -20.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 左上腕ロール (LeftArm_Roll_Joint)  x: -45(右) ~ +45(左)
    # ----------------------------------------------------------------

    @staticmethod
    def left_arm_roll(rx: float, *, rotate_time: int = 250) -> MiracleCommand:
        """左腕ロール。rx の範囲は -45 ~ +45 [deg]。右腕と軸が逆なので符号反転して送信。"""
        return AngleMotionCommands.play_this_angle_motion(
            "left_arm_roll", _LEFT_ARM_ROLL, -rx, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 手首デフォルト (x → 0)
    # ----------------------------------------------------------------

    @staticmethod
    def right_wrist_beat_default(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_wrist_default", _WRIST, 0.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    @staticmethod
    def left_wrist_beat_default(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_wrist_default", _LEFT_WRIST, 0.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 内的ビート - 右腕  (up: upper=-10, forearm=-20, wrist=+25 / down: all→0)
    # ----------------------------------------------------------------

    @staticmethod
    def right_internal_beat_upper(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_internal_upper", _UPPERARM, -10.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    @staticmethod
    def right_internal_beat_forearm(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_internal_forearm", _FOREARM, -20.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    @staticmethod
    def right_internal_beat_wrist(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "right_internal_wrist", _WRIST, 25.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 内的ビート - 左腕  (up: upper=+10, forearm=+20, wrist=+25 / down: all→0)
    # ----------------------------------------------------------------

    @staticmethod
    def left_internal_beat_upper(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_internal_upper", _LEFT_UPPERARM, 10.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    @staticmethod
    def left_internal_beat_forearm(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_internal_forearm", _LEFT_FOREARM, 20.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    @staticmethod
    def left_internal_beat_wrist(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_internal_wrist", _LEFT_WRIST, 25.0, 0.0, 0.0, rotate_time=rotate_time,
        )

    # ----------------------------------------------------------------
    # 左上腕 (LeftArm_Forward_Joint)
    # ----------------------------------------------------------------

    @staticmethod
    def left_upper_beat_default(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_upper_beat_default", _LEFT_UPPERARM, 0.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def left_upper_beat_pull(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_upper_beat_pull", _LEFT_UPPERARM, 5.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )

    @staticmethod
    def left_upper_beat_push(*, rotate_time: int = 250) -> MiracleCommand:
        return AngleMotionCommands.play_this_angle_motion(
            "left_upper_beat_push", _LEFT_UPPERARM, -5.0, 0.0, 0.0,
            rotate_time=rotate_time,
        )
