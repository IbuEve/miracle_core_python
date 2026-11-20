"""
core/miracle/posture/arm/internal_posture.py

internal（手を自分＝胸の中心へ向ける）姿勢。hand="right"|"left" で左右ミラー。
ビートは up→down→back の 3 フェーズ（FrontPosture/SidePosture と同じ構成）。

base 角は t∈[0,1] で ArmRoll / ForeArmRoll を連動抽選（"ぽさ"を出す）。右手基準値:
  ArmRoll      : -30 → -15（外に開く）
  ForeArmRoll  : -45 → -22.5（開いた分、掌を自分向きに保つ）
  ForeArm_Fwd  : -45 固定
抽選は internal へ遷移して来た瞬間（= インスタンス生成時）に 1 回。
左右ミラー: ArmRoll/ForeArmRoll/ForeArm_Forward は sign で反転（前後・ロール系）。
手首（Hand_Joint）は同符号（FrontPosture と同じ規則）。

頭（頷き）: Front/Side と同じ BODY（Spine/Head/Neck）を毎ビートで
  down→body_forward / back→body_reset。

リーン（重心）: Front/Side のように毎ビートで戻すのではなく、
  「話しているうちに少し楽な姿勢へ重心を寄せる」イメージで、
  生成時に left/right を 1 回抽選し、pose() で即座に適用する。
  以後 LEAN_SHIFT_MIN〜MAX 回に 1 回 反対側へトグルする
  （それ以外のビートでは保持＝lean_reset しない）。
  internal から離れるときは呼び出し側が lean_reset する（sample.py 側）。
"""
from __future__ import annotations

import random

from .base import Joint, Posture, hand_part, hand_sign
from ..util import Sender


class InternalPosture(Posture):
    name = "internal"

    # 頷き（前傾）させる胴体部位 (part, deg)。Front/Side と同じ値。
    BODY = [("Spine_Joint", 0.0), ("Head_Joint", 10.0), ("Neck_Joint", 10.0)]
    LEAN_DEGREE = 5.0   # 重心シフトの角度

    LEAN_SHIFT_MIN = 5  # 重心を切り替えるまでのビート数（最小）
    LEAN_SHIFT_MAX = 7  # 重心を切り替えるまでのビート数（最大）

    def __init__(self, tx: Sender, hand: str = "right", t: float | None = None) -> None:
        """t を渡さなければ生成時に 1 回抽選（in/out → internal 遷移のタイミング相当）。"""
        super().__init__(tx)
        self.hand = hand
        self.sign = hand_sign(hand)
        if t is None:
            t = random.random()
        h, s = hand, self.sign
        arm_roll     = (-30.0 + 15.0 * t) * s    # -30 → -15（右手基準）
        forearm_roll = (-45.0 + 22.5 * t) * s    # -45 → -22.5（同じ t で連動）
        self._joints = [
            Joint(hand_part(h, "Arm_Roll_Joint"),       arm_roll,      -6.7 * s),   # 10×30/45（可動小）
            Joint(hand_part(h, "ForeArm_Forward_Joint"), -45.0 * s,    -20.0 * s),
            Joint(hand_part(h, "ForeArm_Roll_Joint"),   forearm_roll, -10.0 * s),
            Joint(hand_part(h, "Hand_Joint"),           0.0,          +20.0),  # 姿勢0・ビート+10（同符号）
        ]

        # 重心（リーン）: 開始side を1回抽選。以後 N ビートごとに反対側へトグル。
        self.lean_direction = random.choice(("left", "right"))
        self._beat_count = 0
        self._next_shift = random.randint(self.LEAN_SHIFT_MIN, self.LEAN_SHIFT_MAX)

    def joints(self):
        return self._joints

    def pose(self, *, ms: int | None = None) -> None:
        """姿勢（関節）に加え、抽選済みの lean_direction へリーンも適用する。"""
        super().pose(ms=ms)
        self._tx.lean_to(self.lean_direction, self.LEAN_DEGREE, ms if ms is not None else self.move_ms)

    # ── ビート（internal の引数: height / ms） ──────────────────────────────
    def up(self, *, height: float = 1.0, ms: int | None = None) -> None:
        self._tx.beat_up(self._joints, height, ms if ms is not None else self.up_ms)

    def down(self, *, ms: int | None = None) -> None:
        ms = ms if ms is not None else self.down_ms
        self._tx.beat_down(self._joints, ms)
        self._tx.body_forward(self.BODY, ms)   # 頷き

        # 重心: N ビートごとに反対側へトグル（それ以外は保持＝何もしない）。
        self._beat_count += 1
        if self._beat_count >= self._next_shift:
            self.lean_direction = "left" if self.lean_direction == "right" else "right"
            self._tx.lean_to(self.lean_direction, self.LEAN_DEGREE, ms)
            self._beat_count = 0
            self._next_shift = random.randint(self.LEAN_SHIFT_MIN, self.LEAN_SHIFT_MAX)

    def back(self, *, ms: int | None = None) -> None:
        ms = ms if ms is not None else self.down_ms
        self._tx.body_reset(self.BODY, ms)     # 頷き戻し（リーンは保持＝reset しない）
