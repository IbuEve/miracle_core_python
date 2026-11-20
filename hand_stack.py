"""
hand_stack.py

両手（左/右）の「出し入れ」をスタック(LIFO)で管理する状態クラス。通信はしない。

物理制約:
  手を「しまう(in)」と上に重なる → 最後にしまった手が一番上。
  「出す(out)」のは一番上の手だけ（下の手を出すと上の手に引っかかって壊れる）。
  → tuck(in)=push / release(out)=pop（top のみ）の LIFO。

使い方（呼ぶ側で can_* / top を確認してから遷移を呼ぶ。違反は ValueError）:
    hands = HandStack()
    if hands.can_in(Hand.RIGHT):
        ...motion...
        hands.tuck(Hand.RIGHT)
    if hands.can_out(Hand.RIGHT):   # = RIGHT が top のときだけ True
        ...motion...
        hands.release(Hand.RIGHT)
"""
from __future__ import annotations

from enum import Enum


class Hand(Enum):
    LEFT = "left"
    RIGHT = "right"

    @property
    def other(self) -> "Hand":
        return Hand.RIGHT if self is Hand.LEFT else Hand.LEFT


class HandStack:
    """しまった手のスタック（bottom→top = しまった順）。両手 OUT（空）で開始。"""

    def __init__(self) -> None:
        self._stack: list[Hand] = []

    # ── 状態参照（public） ──────────────────────────────────────────────
    @property
    def stack(self) -> list[Hand]:
        """bottom→top（しまった順）のコピー。"""
        return list(self._stack)

    @property
    def top(self) -> Hand | None:
        """次に out できる手（最後にしまった手）。空（both out）なら None。"""
        return self._stack[-1] if self._stack else None

    def is_in(self, hand: Hand) -> bool:
        """しまってある？"""
        return hand in self._stack

    def is_out(self, hand: Hand) -> bool:
        return hand not in self._stack

    # ── 可否判定（遷移を呼ぶ前にこれで確認する） ─────────────────────────
    def can_in(self, hand: Hand) -> bool:
        """出ている手はしまえる。"""
        return self.is_out(hand)

    def can_out(self, hand: Hand) -> bool:
        """一番上（最後にしまった手）だけ出せる。"""
        return self.top is hand

    # ── 状態遷移（can_*/top で確認してから呼ぶ。違反は例外） ─────────────
    def tuck(self, hand: Hand) -> None:
        """in: push。すでに in の手を tuck したら ValueError。"""
        if not self.can_in(hand):
            raise ValueError(f"{hand.value} は既に in です（tuck 不可）")
        self._stack.append(hand)

    def release(self, hand: Hand) -> None:
        """out: pop。top でない手を release したら ValueError。"""
        if not self.can_out(hand):
            top = self.top.value if self.top else "なし(both out)"
            raise ValueError(f"{hand.value} は top でないので out 不可（top={top}）")
        self._stack.pop()

    def reset(self) -> None:
        """全部 out（スタックを空に）。"""
        self._stack.clear()

    def __str__(self) -> str:
        names = [h.value for h in self._stack]
        top = self.top.value if self.top else None
        return f"HandStack(bottom→top={names}, top={top})"
