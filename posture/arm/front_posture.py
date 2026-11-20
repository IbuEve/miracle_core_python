"""
core/miracle/posture/arm/front_posture.py

out（差し出し）姿勢。hand="right"|"left" で左右ミラー。

ビートは up→down→back の 3 フェーズ:
  up   … 腕を peak へ ＋ ロール（ArmRoll/ForeArmRoll）を差し出し目標へ向けて半分（遷移）
  down … 腕を 0 へ ＋ ロールを差し出し目標へ到達 ＋ 胴体前傾（頷き）＋ 体リーン
  back … 胴体・リーンを 0 へ戻す（ロールは差し出し位置に保持）

差し出し位置（ArmRoll=方向 / ForeArmRoll=手首角）は per-beat で変わるので、
ビート前に aim(v, forearm_base) で解決済みの値を渡す。抽選は呼び出し側の政策。
  - ArmRoll      = clamp(v, 内側 -INNER / 外側 +OUTER を hand の符号で)
  - ForeArmRoll  = forearm_base × sign（手首角）
aim を呼ばなければ目標 0＝external 姿勢でその場ビート（後方互換）。

左右ミラー: ArmRoll/ForeArmRoll/Arm_Forward/ForeArm_Forward は sign で反転。手首 x は同符号。
リーンの degree / direction は発火する down/back の引数で per-call に受ける（両手で共有）。
"""
from __future__ import annotations

from .base import Joint, Posture, hand_part, hand_sign


class FrontPosture(Posture):
    name = "out"

    # 頷き（前傾）させる胴体部位 (part, deg)。左右共通（hand 非依存）。
    BODY = [("Spine_Joint", 0.0), ("Head_Joint", 10.0), ("Neck_Joint", 10.0)]
    LEAN_DEGREE = 5.0   # lean_degree 省略時の既定

    # 差し出し ArmRoll のクランプ（右手基準）: 内側 -10 / 外側 +30（交差衝突回避）
    OUT_ROLL_OUTER = 30.0
    OUT_ROLL_INNER = 10.0

    def __init__(self, tx, hand: str = "right") -> None:
        super().__init__(tx)
        self.hand = hand
        self.sign = hand_sign(hand)
        self._arm_roll = 0.0       # 差し出し ArmRoll（aim で更新）
        self._forearm_roll = 0.0   # 差し出し ForeArmRoll（手首角）

    def aim(self, v: float, forearm_base: float) -> None:
        """ビート前に差し出し目標を決める。v は物理方向（両手共通）、forearm_base は右手基準。"""
        sign = self.sign
        outer = self.OUT_ROLL_OUTER * sign
        inner = -self.OUT_ROLL_INNER * sign
        lo, hi = (inner, outer) if inner <= outer else (outer, inner)
        self._arm_roll = max(lo, min(hi, v))          # 各手の内外でクランプ
        self._forearm_roll = forearm_base * sign

    def joints(self):
        h, s = self.hand, self.sign
        return [
            # 差し出しロール（遷移関節 beat_delta=0）: 現在→目標へビート中に EASE で運ぶ。
            Joint(hand_part(h, "Arm_Roll_Joint"),     self._arm_roll,     0.0),
            Joint(hand_part(h, "ForeArm_Roll_Joint"), self._forearm_roll, 0.0),
            # ビートで上下する腕関節（beat_delta あり）。前後系は左右反転、手首は同符号。
            Joint(hand_part(h, "Arm_Forward_Joint"),     0.0, +10.0 * s),
            Joint(hand_part(h, "ForeArm_Forward_Joint"), 0.0, -20.0 * s),
            Joint(hand_part(h, "Hand_Joint"),            0.0, +5.0),
        ]

    # ── ビート（out の引数: height / ms / lean_degree / lean_direction） ──────
    def up(self, *, height: float = 1.0, ms: int | None = None) -> None:
        self._tx.beat_up(self.joints(), height, ms if ms is not None else self.up_ms)

    def down(self, *, ms: int | None = None,
             lean_degree: float | None = None, lean_direction: str = "right") -> None:
        ms = ms if ms is not None else self.down_ms
        deg = lean_degree if lean_degree is not None else self.LEAN_DEGREE
        self._tx.beat_down(self.joints(), ms)          # 腕→0 / ロール→差し出し目標
        self._tx.body_forward(self.BODY, ms)           # 頷き（両手共有・id=part で置換）
        self._tx.lean_to(lean_direction, deg, ms)      # リーン（両手共有）

    def back(self, *, ms: int | None = None,
             lean_degree: float | None = None, lean_direction: str = "right") -> None:
        ms = ms if ms is not None else self.down_ms
        deg = lean_degree if lean_degree is not None else self.LEAN_DEGREE
        self._tx.body_reset(self.BODY, ms)
        self._tx.lean_reset(lean_direction, deg, ms)
