"""
TactBase Miracle Posture Module
===============================
姿勢（pose）と、その姿勢のビート（up/down/back フェーズ）を socket へ
組み立て送信する Posture クラス階層。

役割分担:
  util.py … 動作を作る送信パーツ（send_angle / send_rollpose / beat_* / body_* / lean_* / orient*）
  arm/    … Arm（腕）の姿勢。base.py（抽象表現 pose 共通 + joints() 要求）+ 各 posture
  body/   … Body（向き）の front/side
  head/   … head（向き）の front/side
  eye/    … eye（向き）の front/side（any は今後追加）

  arm.Posture(ABC)
    ├ arm.FrontPosture    : front（right_external）。up/down/back（頷き＋リーン）
    ├ arm.InPosture       : in（しまう。pose のみ）
    ├ arm.InternalPosture : internal（自分に向ける。up/down 2 フェーズ）
    └ arm.SidePosture     : side（画面を指す。pose のみ）
"""

from .util import Sender, send_angle, send_controller, send_playmotion, send_rollpose
from .arm import (
    FrontPosture,
    InPosture,
    InternalPosture,
    Joint,
    Posture,
    SidePosture,
    hand_part,
    hand_sign,
)
from . import body, eye, head

__all__ = [
    "Posture",
    "Joint",
    "hand_part",
    "hand_sign",
    "Sender",
    "send_angle",
    "send_rollpose",
    "send_playmotion",
    "send_controller",
    "FrontPosture",
    "InPosture",
    "InternalPosture",
    "SidePosture",
    "body",
    "head",
    "eye",
]
