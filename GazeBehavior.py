"""
GazeBehavior
============
Head + Eye の視線状態を生成するクラス。
コマンド生成のみを行い、送信は呼び出し側が担う。

Usage:
    behavior = GazeBehavior(default_x=0.0, default_y=1.4, default_z=1.5)

    state = behavior.random()
    await client.send_json_command(state.head_cmd.key, state.head_cmd.value)
    await client.send_json_command(state.eye_cmd.key,  state.eye_cmd.value)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .CommandBuilder import MiracleCommand, MiracleCommands


@dataclass(frozen=True)
class GazeState:
    """
    生成された視線状態。送信用コマンドと座標値の両方を持つ。
    座標値は GUI 側でキャンバスを更新するために使用する。
    """
    head_cmd: MiracleCommand
    eye_cmd:  MiracleCommand
    main_x:   float
    main_y:   float
    fine_dx:  float
    fine_dy:  float


class GazeBehavior:
    """
    視線の振る舞いを定義するクラス。
    GazeState（コマンド + 座標）を返す静的でないメソッドを提供する。

    Parameters
    ----------
    default_x, default_y, default_z:
        デフォルト（正面）の注視ワールド座標。
    head_radius:
        ランダム時に Head が default から動く最大半径 [m]。
    eye_extra:
        ランダム時に Head 位置からさらに Eye を同方向へずらす距離 [m]。
    angular_speed:
        EyeController / HeadController の角速度 [deg/sec]。
    """

    def __init__(
        self,
        default_x: float,
        default_y: float,
        default_z: float,
        *,
        head_radius: float = 0.1,
        eye_extra: float = 0.2,
        angular_speed: float = 90.0,
    ) -> None:
        self.default_x = default_x
        self.default_y = default_y
        self.default_z = default_z
        self.head_radius = head_radius
        self.eye_extra = eye_extra
        self.angular_speed = angular_speed

    # ----------------------------------------------------------------

    def random(self) -> GazeState:
        """
        ランダムな視線状態を生成する。
        Head は default から head_radius 以内のランダム方向へ移動し、
        Eye はその方向にさらに eye_extra だけ追加でずれる。
        """
        theta = random.uniform(0.0, 2.0 * math.pi)
        r_head = random.uniform(0.0, self.head_radius)
        cos_t, sin_t = math.cos(theta), math.sin(theta)

        main_x = self.default_x + r_head * cos_t
        main_y = self.default_y + r_head * sin_t
        fine_dx = self.eye_extra * cos_t
        fine_dy = self.eye_extra * sin_t

        return GazeState(
            head_cmd=MiracleCommands.head_controller(
                main_x, main_y, self.default_z,
                angular_speed=self.angular_speed,
            ),
            eye_cmd=MiracleCommands.eye_controller(
                main_x + fine_dx, main_y + fine_dy, self.default_z,
                angular_speed=self.angular_speed,
            ),
            main_x=main_x,
            main_y=main_y,
            fine_dx=fine_dx,
            fine_dy=fine_dy,
        )

    def default(self) -> GazeState:
        """デフォルト位置への視線状態を返す（fine offset なし）。"""
        return GazeState(
            head_cmd=MiracleCommands.head_controller(
                self.default_x, self.default_y, self.default_z,
                angular_speed=self.angular_speed,
            ),
            eye_cmd=MiracleCommands.eye_controller(
                self.default_x, self.default_y, self.default_z,
                angular_speed=self.angular_speed,
            ),
            main_x=self.default_x,
            main_y=self.default_y,
            fine_dx=0.0,
            fine_dy=0.0,
        )
