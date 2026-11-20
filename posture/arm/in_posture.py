"""
core/miracle/posture/arm/in_posture.py

in（しまう）姿勢。hand="right"|"left" で左右ミラー。
pose（tuck 位置へ戻す）だけを持ち、ビートは無し（up/down/back を実装しない）。

tuck 位置（右手基準。左手は sign で反転）:
  ArmRoll      = -45（bottom：一番下にしまう手）/ -15（top：既にしまった手の上に重ねる手）
  ForeArmRoll  = -90
  ForeArm_Fwd  = 0   （internal の -45 などを残さないよう戻す）

top=True のとき ArmRoll を浅く（-15）して、下にある手との衝突を避ける。
"""
from __future__ import annotations

from .base import Joint, Posture, hand_part, hand_sign

IN_ARM_ROLL_FULL = -45.0   # bottom（深くしまう）
IN_ARM_ROLL_TOP  = -20.0   # top（浅く重ねる）
IN_FOREARM_ROLL  = -90.0


class InPosture(Posture):
    name = "in"

    def __init__(self, tx, hand: str = "right", top: bool = False) -> None:
        """top=True: 既に下にしまった手があり、その上に重ねる側（ArmRoll を浅く）。"""
        super().__init__(tx)
        self.hand = hand
        sign = hand_sign(hand)
        self._arm_roll = (IN_ARM_ROLL_TOP if top else IN_ARM_ROLL_FULL) * sign
        self._fore_roll = IN_FOREARM_ROLL * sign

    def joints(self):
        h = self.hand
        return [
            Joint(hand_part(h, "Arm_Roll_Joint"),     self._arm_roll),
            Joint(hand_part(h, "ForeArm_Roll_Joint"), self._fore_roll),
            Joint(hand_part(h, "ForeArm_Forward_Joint"), 0.0),
        ]
