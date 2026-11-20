"""
core/miracle/posture/arm/side_posture.py

side（画面を指す）姿勢。hand="right"|"left" で左右ミラー。

pose で以下を行う:
  - Arm_Roll_Joint     = ARM_ROLL_DEG * sign（側方へロール）
  - ForeArm_Roll_Joint = 0（手首角。pose 時点では未抽選のため 0。ビートで aim の目標へ）
  - Arm_Forward_Joint  = 0（ビートの叩き関節。pose では 0）
  - ForeArm_Forward_Joint = 0（in/internal の前腕曲げが残らないようリセット）
  - Hand_Joint         = HAND_Z_DEG * sign（z 軸。手首を傾ける）/ HAND_X_DEG（x 軸。手を少し下げる）

向き（Body/Head/Eye）は posture/body, posture/head, posture/eye の責務（このクラスでは行わない）。

joints() は他姿勢から来たときに残り得る関節（ForeArm_Roll/ForeArm_Forward）も
明示的に列挙する＝side姿勢のフル指定（FrontPosture/InPosture と同じ流儀）。
playthisanglemotion は id=part で「置換」されるため、ここに列挙した part は
前の姿勢の値に関わらず必ず上書きされる。

ビートは up→down→back の 3 フェーズ（FrontPosture と同じ構成）:
  - Arm_Roll_Joint / ForeArm_Forward_Joint / ForeArm_Roll_Joint は
    「目標値が呼び出し側で決まる」関節。ビート前に
    aim(arm_roll, forearm_fwd, forearm_base) で目標を渡す（抽選は呼び出し側の
    政策。FrontPosture.aim() と同じパターン。forearm_base は右手基準値で、
    ForeArm_Roll_Joint には forearm_base * sign が入る）。
  - Arm_Roll_Joint / ForeArm_Roll_Joint は遷移関節（beat_delta=0）: 現在 → aim
    の目標へ EASE で運ぶ（差し出しロールと同じ）。
  - Arm_Forward_Joint / ForeArm_Forward_Joint / Hand_Joint は FrontPosture と
    同じ beat_delta（+10*s / -20*s / +5.0）で叩く。ForeArm_Forward_Joint の
    resting（angle）のみ aim() で可変。
  - down/back は body_forward/lean_to による頷き＋体リーンを伴う
    （lean_direction はパラメータ化。side では呼び出し側が "right" を渡す）。
"""
from __future__ import annotations

from .base import Joint, Posture, hand_part, hand_sign


class SidePosture(Posture):
    name = "side"

    ARM_ROLL_DEG = 45.0   # Arm_Roll_Joint（x 軸）
    HAND_X_DEG = -15.0    # Hand_Joint（x 軸。手を少し下げる。ビートで叩く）
    HAND_Z_DEG = -20.0    # Hand_Joint（z 軸。手首を傾ける。ビートなし）

    # 頷き（前傾）させる胴体部位 (part, deg)。FrontPosture と同じ値を独自定義。
    BODY = [("Spine_Joint", 0.0), ("Head_Joint", 10.0), ("Neck_Joint", 10.0)]
    LEAN_DEGREE = 5.0   # lean_degree 省略時の既定

    JITTER_DEG = 5.0    # aim() の目標値ジッター幅の目安 [deg]（抽選は呼び出し側）

    def __init__(self, tx, hand: str = "right") -> None:
        super().__init__(tx)
        self.hand = hand
        self.sign = hand_sign(hand)
        self._arm_roll = self.ARM_ROLL_DEG * self.sign       # Arm_Roll_Joint の目標（aim で更新）
        self._forearm_fwd = 0.0                               # ForeArm_Forward_Joint の resting（aim で更新）
        self._forearm_roll = 0.0                              # ForeArm_Roll_Joint の目標（aim で更新）

    def aim(self, arm_roll: float, forearm_fwd: float, forearm_base: float) -> None:
        """ビート前に Arm_Roll_Joint / ForeArm_Forward_Joint / ForeArm_Roll_Joint の
        目標を決める。抽選（current ± JITTER_DEG や手首角3択等）は呼び出し側の政策。
        forearm_base は右手基準の手首角で、sign を掛けて ForeArm_Roll_Joint に渡す
        （FrontPosture.aim() と同じ規則）。"""
        self._arm_roll = arm_roll
        self._forearm_fwd = forearm_fwd
        self._forearm_roll = forearm_base * self.sign

    def joints(self):
        h, s = self.hand, self.sign
        return [
            # 差し出しロールと同じ遷移関節（beat_delta=0）: 現在→aim の目標へ EASE で運ぶ。
            Joint(hand_part(h, "Arm_Roll_Joint"), self._arm_roll, 0.0),
            Joint(hand_part(h, "ForeArm_Roll_Joint"), self._forearm_roll, 0.0),
            # ビートで上下する腕関節（FrontPosture と同じ beat_delta）。
            Joint(hand_part(h, "Arm_Forward_Joint"), 0.0, +15.0 * s),
            Joint(hand_part(h, "ForeArm_Forward_Joint"), self._forearm_fwd, -30.0 * s),
            Joint(hand_part(h, "Hand_Joint"), self.HAND_X_DEG, +5.0, axis="x",
                  angle2=self.HAND_Z_DEG * s, axis2="z"),
        ]

    # ── ビート（side の引数: height / ms / lean_degree / lean_direction） ────
    def up(self, *, height: float = 1.0, ms: int | None = None) -> None:
        self._tx.beat_up(self.joints(), height, ms if ms is not None else self.up_ms)

    def down(self, *, ms: int | None = None,
             lean_degree: float | None = None, lean_direction: str = "right") -> None:
        ms = ms if ms is not None else self.down_ms
        deg = lean_degree if lean_degree is not None else self.LEAN_DEGREE
        self._tx.beat_down(self.joints(), ms)          # 腕→resting / ロール→aim の目標
        self._tx.body_forward(self.BODY, ms)           # 頷き
        self._tx.lean_to(lean_direction, deg, ms)       # リーン

    def back(self, *, ms: int | None = None,
             lean_degree: float | None = None, lean_direction: str = "right") -> None:
        ms = ms if ms is not None else self.down_ms
        deg = lean_degree if lean_degree is not None else self.LEAN_DEGREE
        self._tx.body_reset(self.BODY, ms)
        self._tx.lean_reset(lean_direction, deg, ms)
