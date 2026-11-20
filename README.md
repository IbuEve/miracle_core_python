# core/miracle

MiracleHuman に Python からコマンドを送るためのライブラリ。ここには基本の使い方だけ書く。

コマンドそのものの仕様（JSON の各項目、関節名、座標系など）は [docs/](./docs/README.md) を参照。

## 1. import

TactBase のルートをパスに通してから import する。

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # exp/expXXX/foo.py から TactBase へ

from core.miracle import MiracleAsyncClient, MiracleCommands, AngleMotionCommands
```

## 2. 接続

Miracle を起動しておき、ControllerASync（21000 番）に接続する。送信は非同期なので `asyncio` の中で使う。

```python
import asyncio

async def main():
    async with MiracleAsyncClient("127.0.0.1", 21000) as client:
        ...  # ここで送る

asyncio.run(main())
```

受信したい場合は `MiracleAsyncClient(on_receive=print)` のようにコールバックを渡す。

## 3. 送り方の基本

`MiracleCommands` / `AngleMotionCommands` のメソッドは、すべて `MiracleCommand(key, value)` を返す。
value の型で送る関数を使い分ける。

| value | 送る関数 |
|---|---|
| `str` | `client.send_command(cmd.key, cmd.value)` |
| `dict` | `client.send_json_command(cmd.key, cmd.value)` |

文字列をそのまま送りたいときは `client.send_raw("playmotion=greeting")` を使う（改行は自動で付く）。

## 4. 定義済みモーションを指定して動かす（playmotion）

```python
cmd = MiracleCommands.play_motion(["greeting"])
await client.send_command(cmd.key, cmd.value)

# 続けて再生する。数字は速度スケール（0.1 遅い 〜 10.0 速い）
cmd = MiracleCommands.play_motion([("handbeat-mid-righthand", 1), ("lefthandbaseposition", 2)])
await client.send_command(cmd.key, cmd.value)

# 再生中のモーションを全部止める
cmd = MiracleCommands.reset_all_motions()
await client.send_command(cmd.key, cmd.value)
```

定義済みアクションは `MiracleCommands.play_action("action_id")` で再生する。

## 5. JSON を送る（playthismotion など）

自分で組んだ dict は、コマンド名を指定して `send_json_command` で送る。

```python
payload = {
    "id": "right_hand_tmp",
    "motionPartName": "RightHandController",
    "motionData": [{
        "id": "0",
        "targetMotionMode": 1,
        "motionTowardObject": "BodyController",
        "targetPoint": {"x": 0.0, "y": 0.0, "z": 0.5},
        "translateTime": 850,
        "translateSpeed": -1,
        "keepTime": 0,
    }],
}
await client.send_json_command("playthismotion", payload)
```

JSON ファイルを送るときも同じ形で送る。

```python
import json
payload = json.loads(Path("motion.json").read_text(encoding="utf-8"))
await client.send_json_command("playthisanglemotion", payload)
```

Unity から書き出した JSON には、送らなくてよい内部参照の項目が入っている。それを除いて送る例は [exp/exp001/test_anglemotion.py](../../exp/exp001/test_anglemotion.py)。

## 6. アングルモーション（関節角を直接送る）

```python
cmd = AngleMotionCommands.play_this_angle_motion(
    "my_wrist",          # id（同じ id で送り直すと上書きになる）
    "RightHand_Joint",   # 関節名
    0.0, 0.0, 20.0,      # rx, ry, rz [deg]
    rotate_time=250,     # 到達時間 [ms]
)
await client.send_json_command(cmd.key, cmd.value)
```

`right_wrist_beat_z_down()` など、よく使う角度はメソッドとして用意してある（[AngleMotionBuilder.py](./AngleMotionBuilder.py)）。
value は dict なので `send_json_command` で送る（ファイル内の docstring にある `send_command` の例は誤り）。

## 7. その他のコマンド

視線・頭・手（`eye_controller` / `head_controller` / `right_hand_controller`）、表情（`set_face`）、感情、オブジェクト生成なども同じ形で送れる。
一覧は [CommandBuilder.py](./CommandBuilder.py) を見る。

## 使用例

- [exp/exp002_talkMiracle/updown_command_sender.py](../../exp/exp002_talkMiracle/updown_command_sender.py)：`play_motion` と `play_this_action` を送る
- [exp/exp005_intentionmotion/head_controller_test.py](../../exp/exp005_intentionmotion/head_controller_test.py)：入力した座標へ頭を向ける
- [exp/exp001/angle_slider_gui.py](../../exp/exp001/angle_slider_gui.py)：スライダーで関節角を送る
