"""
miracle/posture/arm/base.py

姿勢（Posture）の抽象基底。役割分担:
  - base（ここ）  : 抽象表現。joints() を要求し、pose()（全姿勢共通）を提供する。
  - util.Sender   : 送信＋現在角の保持。呼び出し側で 1 個作り、全 posture に渡して共有する。
  - 各 posture     : Sender(self._tx) を組み合わせて up()/down()/back() を実装する。

ビートのフェーズ（up/down/back）は base では宣言しない。
  - ビートを持たない姿勢（in）は実装しなくてよい。
  - 持つ姿勢（internal/out）が、それぞれ必要なパラメータで実装する。
  - timing（フェーズ間の待ち）は呼び出し側が刻む。playthisaction は使わない。

注意（呼び出し側の約束）:
  - pose() だけは全姿勢で無引数に揃える → `cur: Posture` のまま呼べる。
  - up()/down()/back() は型が分かる文脈でのみ呼ぶ（姿勢ごとに引数が違ってよい）。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..util import Sender

# ── 左右ミラー（hand="right"|"left"） ──────────────────────────────────────────
_PREFIX = {"right": "Right", "left": "Left"}
_SIGN = {"right": 1.0, "left": -1.0}


def hand_part(hand: str, suffix: str) -> str:
    """例: ("right","Arm_Roll_Joint") → "RightArm_Roll_Joint"。"""
    return _PREFIX[hand] + suffix


def hand_sign(hand: str) -> float:
    """左右ミラー符号。right=+1 / left=-1。
    左右で符号が逆になる関節（ArmRoll/ForeArmRoll/前後系）に掛ける。手首 x は掛けない。"""
    return _SIGN[hand]


@dataclass(frozen=True)
class Joint:
    """
    姿勢を構成する 1 関節。

    part       : 関節名（例 "RightArm_Roll_Joint"）
    angle      : 姿勢としての目標角 [deg]
    beat_delta : ビートで上げる量 [deg]（0 ならビートでは動かさない）
    axis       : 角度を適用する軸（"x" | "y" | "z"）。既定は "x"。

    angle2/axis2/beat_delta2 : 2 軸目（任意）。同じ part に 2 軸を同時指定したい場合に使う
    （playthisanglemotion は id=part で targetRotation 全体を置換するため、
     2 軸目を別の Joint として送ると 1 軸目が 0 で上書きされてしまう）。
    axis2 が None なら未使用。
    """
    part: str
    angle: float
    beat_delta: float = 0.0
    axis: str = "x"
    angle2: float | None = None
    axis2: str | None = None
    beat_delta2: float = 0.0


class Posture(ABC):
    """姿勢の抽象基底。共有 Sender を受け取り、pose（共通）を組み立て送信する。"""

    name: str = "posture"
    move_ms: int = 600   # pose 遷移の所要時間
    up_ms: int = 180     # up フェーズ（各 posture が使う既定値）
    down_ms: int = 220   # down フェーズ

    def __init__(self, tx: Sender) -> None:
        self._tx = tx   # 全姿勢で共有する Sender（socket＋現在角を保持）

    @abstractmethod
    def joints(self) -> list[Joint]:
        """この姿勢を構成する関節（角度＋ビート振幅）。具象が実装する。"""

    # ── pose（全姿勢共通） ──────────────────────────────────────────────────
    def pose(self, *, ms: int | None = None) -> None:
        """各関節を angle へ動かす＝この姿勢になる。ms 省略時は move_ms。id=part で送信。"""
        ms = ms if ms is not None else self.move_ms
        for j in self.joints():
            self._tx.angle(j.part, j.angle, ms, axis=j.axis,
                            target_deg2=j.angle2, axis2=j.axis2)
