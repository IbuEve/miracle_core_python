"""
core/miracle/posture/body/body_posture.py

front/side（Bodyの向き）。BodyControllerのみを動かす。
"""
from __future__ import annotations

from ..util import Sender

BODY_DEG = 30.0
MOVE_MS = 600


def to_front(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("BodyController", 0.0, ms=ms, speed_deg=BODY_DEG)


def to_side(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("BodyController", BODY_DEG, ms=ms)
