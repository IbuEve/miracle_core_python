"""
core/miracle/posture/head/head_posture.py

front/shallow1/shallow2/side（headの向き）。HeadControllerのみを動かす。
"""
from __future__ import annotations

from ..util import Sender, gaze_y_for_deg

HEAD_DEG_FRONT    = 0.0
HEAD_DEG_SHALLOW0 = 7.0
HEAD_DEG_SHALLOW1 = 15.0
HEAD_DEG_SHALLOW2 = 30.0
HEAD_DEG          = 45.0
MOVE_MS = 600


def to_front(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("HeadController", HEAD_DEG_FRONT, y=gaze_y_for_deg(HEAD_DEG_FRONT), ms=ms, speed_deg=HEAD_DEG)


def to_shallow0(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("HeadController", HEAD_DEG_SHALLOW0, y=gaze_y_for_deg(HEAD_DEG_SHALLOW0), ms=ms)


def to_shallow1(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("HeadController", HEAD_DEG_SHALLOW1, y=gaze_y_for_deg(HEAD_DEG_SHALLOW1), ms=ms)


def to_shallow2(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("HeadController", HEAD_DEG_SHALLOW2, y=gaze_y_for_deg(HEAD_DEG_SHALLOW2), ms=ms)


def to_side(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("HeadController", HEAD_DEG, y=gaze_y_for_deg(HEAD_DEG), ms=ms)


def to_deg(tx: Sender, deg: float, *, ms: int = MOVE_MS) -> None:
    """任意の角度degへ向ける（高さはgaze_y_for_degで自動算出）。SideGlance復帰時など。"""
    tx.orient_one("HeadController", deg, y=gaze_y_for_deg(deg), ms=ms)
