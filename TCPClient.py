"""
MiracleHuman TCP Client (ControllerASync)
Port: 21000
- 非同期通信（TCP）
- コマンドのフッターは改行コード（\n）
- 文字コードは UTF-8
"""

import asyncio
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class MiracleAsyncClient:
    """
    MiracleHuman ControllerASync (port 21000) 向け非同期TCPクライアント。
    接続・送信・受信コールバックを提供する。
    """

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 21000
    ENCODING = "utf-8"
    FOOTER = "\n"

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        on_receive: Optional[Callable[[str], None]] = None,
    ):
        self.host = host
        self.port = port
        self.on_receive = on_receive  # 受信時に呼ばれるコールバック

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._receive_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # 接続 / 切断
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """サーバに接続し、受信ループを開始する。"""
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
        logger.info("Connected to %s:%d", self.host, self.port)
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def disconnect(self) -> None:
        """受信ループを停止し、接続を閉じる。"""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None

        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None

        logger.info("Disconnected from %s:%d", self.host, self.port)

    # ------------------------------------------------------------------
    # 送信
    # ------------------------------------------------------------------

    async def send_raw(self, message: str) -> None:
        """改行を付けて文字列を送信する。"""
        if self._writer is None:
            raise RuntimeError("Not connected. Call connect() first.")

        data = (message + self.FOOTER).encode(self.ENCODING)
        self._writer.write(data)
        await self._writer.drain()
        logger.debug("Sent: %s", message)

    async def send_command(self, command: str, value: str) -> None:
        """
        `command=value\\n` 形式で送信する。

        Examples
        --------
        await client.send_command("arousal", "1.0")
        await client.send_command("setface", '{"id": "FullSmile", "speedScale": 1}')
        """
        await self.send_raw(f"{command}={value}")

    async def send_json_command(self, command: str, payload: dict) -> None:
        """
        dictをJSON文字列に変換して `command={...}\\n` 形式で送信する。

        Examples
        --------
        await client.send_json_command("EyeController", {
            "id": "EyeController",
            "targetMotionMode": 2,
            "targetPoint": {"x": 0.0, "y": 1.2, "z": 1.0},
            "translateAngularSpeed": 90.0,
            "tracking": False,
        })
        """
        import json

        await self.send_raw(f"{command}={json.dumps(payload, separators=(',', ':'))}")

    # ------------------------------------------------------------------
    # 受信ループ
    # ------------------------------------------------------------------

    async def _receive_loop(self) -> None:
        """受信した行ごとに on_receive コールバックを呼び出す。"""
        assert self._reader is not None
        try:
            while True:
                line = await self._reader.readline()
                if not line:
                    logger.info("Connection closed by server.")
                    break
                message = line.decode(self.ENCODING).rstrip(self.FOOTER)
                logger.debug("Received: %s", message)
                if self.on_receive:
                    self.on_receive(message)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Receive error: %s", e)

    # ------------------------------------------------------------------
    # コンテキストマネージャ対応
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "MiracleAsyncClient":
        await self.connect()
        return self

    async def __aexit__(self, *_) -> None:
        await self.disconnect()


# ------------------------------------------------------------------
# 動作確認用サンプル
# ------------------------------------------------------------------

async def _main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    def on_receive(msg: str) -> None:
        print(f"[RECV] {msg}")

    async with MiracleAsyncClient(host="127.0.0.1", port=21000, on_receive=on_receive) as client:
        # 視線を正面に向ける
        await client.send_json_command(
            "EyeController",
            {
                "id": "EyeController",
                "targetMotionMode": 2,
                "targetPoint": {"x": 0.0, "y": 1.2, "z": 1.0},
                "translateAngularSpeed": 90.0,
                "tracking": False,
            },
        )

        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(_main())
