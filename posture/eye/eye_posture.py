"""
miracle/posture/eye/eye_posture.py

front/shallow/side（eyeの向き）。EyeControllerのみを動かす。
any（観客から目線をそらす動き）は Miracle 側のサッケード機能（set_saccade）に任せる。
"""
from __future__ import annotations

from ..util import GAZE_ANGLE_SIDE, Sender, gaze_y_for_deg

EYE_DEG_FRONT   = 0.0
EYE_DEG_SHALLOW = 30.0
EYE_DEG         = GAZE_ANGLE_SIDE  # = 60.0（高さが GAZE_Y_SIDE になる基準角）
MOVE_MS = 600


def to_front(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("EyeController", EYE_DEG_FRONT, y=gaze_y_for_deg(EYE_DEG_FRONT), ms=ms, speed_deg=EYE_DEG)


def to_shallow(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("EyeController", EYE_DEG_SHALLOW, y=gaze_y_for_deg(EYE_DEG_SHALLOW), ms=ms)


def to_side(tx: Sender, *, ms: int = MOVE_MS) -> None:
    tx.orient_one("EyeController", EYE_DEG, y=gaze_y_for_deg(EYE_DEG), ms=ms)


def set_saccade(tx: Sender, enabled: bool) -> None:
    """観客から目線をそらす自動の細かい視線移動（サッケード）の有効/無効を切り替える。"""
    tx.saccade(enabled)
