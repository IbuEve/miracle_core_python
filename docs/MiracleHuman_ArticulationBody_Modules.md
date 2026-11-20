# MiracleHuman の ArticulationBody 制御モジュールと親子関係

## 1. 全体像

MiracleHuman は Unity の `ArticulationBody` を使ってヒューマノイドのジョイントを構成し、その上位に複数の制御モジュールを配置しています。外部からは `EyeController`、`HeadController`、`BodyController`、`RightHandController`、`LeftHandController` などの Controller にコマンドを送り、内部でジョイント角・IK・表情・姿勢揺らぎ・下半身連動などに変換されます。

概念的な階層は次の通りです。

```text
外部 TCP コマンド
  ├─ ControllerASync / ControllerSync
  │   ├─ Motion Controller 群
  │   │   ├─ EyeController
  │   │   ├─ HeadController
  │   │   ├─ BodyController
  │   │   ├─ RightHandController
  │   │   └─ LeftHandController
  │   ├─ Motion / HandMotion / AngleMotion 再生
  │   ├─ FACS / ManualFACS / Blink
  │   ├─ Action 合成
  │   ├─ Emotion / CPG / Emotion2Pose / ListeningBehavior
  │   └─ ModuleControl / Target / Object / Camera / Motor
  └─ Streaming
      ├─ jointstate
      ├─ mentalstate
      ├─ speechstate
      ├─ gaze / pointing / dangerous state
      └─ objects / robots

ArticulationBody ジョイント階層
  ├─ Root / BodyBase / Pelvis / Stance 系
  ├─ SpineYaw / SpinePitch / Spine / BodyController 系
  ├─ Head / HeadController 系
  ├─ LeftEye / RightEye / EyeController 系
  ├─ Right arm / RightHandController / Right fingers
  └─ Left arm / LeftHandController / Left fingers
```

## 2. Motion Controller の親子関係

### EyeController

- 眼球・視線方向を制御します。
- `priority >= 2` の場合、意識的に視線を向ける制御として Blink が連動します。
- `gazeavert`、`saccade`、Blink モジュールと併用されます。
- 親方向として Head の姿勢に影響を受けますが、視線ターゲットとしては独立に指定できます。

### HeadController

- 頭部の向きを制御します。
- EyeController と同じターゲットを見る Action で組み合わせると `gaze` 的な動作になります。
- `Attractiveness` の `Head` によって、対象へ顔を向ける度合いを調整できます。
- 頷きや Listening Behavior では、首だけで角度が足りない場合に Head と Body の連動が起きます。

### BodyController

- 体幹の向き・姿勢を制御します。
- HeadController の親に近い役割を持ち、頭部や腕の到達範囲・向きに影響します。
- `Attractiveness` の `Body` で対象へ体を向ける度合いを調整できます。
- `stancebodyparam` により下半身 / Stance と連動できます。

### RightHandController / LeftHandController

- 腕 IK・手先位置・手先回転・指姿勢を制御します。
- `fingerData` で `RightIndexFinger`、`RightFingers`、`LeftIndexFinger`、`LeftFingers` などを併せて指定できます。
- `MotionOfHand` / `playthishandmotion` では、手の位置座標系と手のひら回転座標系を別々に指定できます。

## 3. 体幹・下半身・姿勢モジュール

### Trunk manual control

```text
trunkjointparam={"part":"SpineYaw", "useManual":true,"angle":40.0, "smoothingSpeed":45.0}\n
```

- `part`: `SpineYaw` / `SpinePitch`
- `useManual`: `false` で自動計算に戻る
- `angle`: 基準からの絶対角度。可動範囲外は制限される
- `smoothingSpeed`: `[deg/sec]`。`-1` でデフォルト

### Stance と BodyController の連動

```text
stancebodyparam={"part":"Pitch", "ratio":0.5}\n
```

- `part`: `Yaw` / `Pitch`
- `ratio`: `0.0`〜`1.0`。大きいほど下半身が BodyController 方向を向き、BodyController の Attractiveness と前傾にも連動します。

### Roll pose

```text
rollpose={"degree":5.0, "direction":"left", "samedirection":true, "rollspeed":20.0}\n
```

- 手動でロール姿勢を変えます。
- 送信すると自動で `Emotion2Pose` は停止します。

### Emotion2Pose

```text
modulecontrol={"moduleName":"Emotion2Pose", "permit": true}\n
```

- 内部状態や感情に基づく姿勢変化を担うモジュールです。
- `rollpose` などの手動姿勢指定と競合しうるため、必要に応じて停止・再開します。

### CPG (Central Pattern Generator)

```text
cpg={"scale":5, "frequency":2, "perlinscale":1}\n
```

- 姿勢や動作に周期的な揺らぎを加えるモジュールです。
- `scale`: 揺らぎの大きさ
- `frequency`: 速さ
- `perlinscale`: Perlin noise の強さ

## 4. 表情・視線・音声連動モジュール

### FACS / ManualFACS

- `setface` で定義済み表情を再生します。
- `setmanualfacs` で Action Unit 相当のパラメータを直接指定します。
- `addfacs` で定義済み FACS の一部パラメータを上書きできます。

### Blink

```text
blink={"duration":500, "intentional":true}\nblinkmodule={"enable":true}\n
```

- 任意タイミングの瞬き、または Blink モジュールの ON/OFF を制御します。
- EyeController の高優先度制御と連動します。

### Listening Behavior

```text
listeningmodule={"enable":true}\n
```

- 対話相手のセンシングや音声韻律に合わせて頷きなどを自動生成します。
- 設定 JSON の `ListeningProsody` ノードで話者の声を解析した Core に接続する必要があります。

## 5. モジュール制御

任意モジュールは次の形式で ON/OFF できます。

```text
modulecontrol={"moduleName":"name", "permit": true}\n
```

例:

```text
modulecontrol={"moduleName":"Emotion2Pose", "permit": false}\n
```

## 6. ArticulationBody ジョイント状態の取得

Streaming の `StateStreamer` でジョイント状態を取得できます。

```text
StateStreamer={"jointstate":[{"jointname":"Pelvis","jointdata":{"xAngle":-0.0002924751,"yAngle":-0.001763284,"zAngle":-0.0001642044,"globalposition":{"x":0,"y":0.464,"z":0},"globalrotation":{"x":0,"y":0,"z":0,"w":1,"euler_x":0,"euler_y":0,"euler_z":0}}}]}
```

`jointstate` の主な項目:

| 項目 | 説明 |
|---|---|
| `jointname` | ジョイント名 |
| `xAngle` / `yAngle` / `zAngle` | 関節初期姿勢からの相対角度 |
| `globalposition` | ジョイントの世界座標位置 |
| `globalrotation` | ジョイントの世界座標回転。Quaternion と Euler を含む |

## 7. 親子関係を意識した制御設計

### 視線だけを動かす

- `EyeController` のみを指定します。
- `priority` を上げると意識的な視線移動として Blink が連動します。

### 目と顔を向ける

- `EyeController` と `HeadController` を同じターゲットに向けます。
- 命名としては `gaze` レベルの Action に相当します。

### 体ごと向ける

- `EyeController`、`HeadController`、`BodyController` を組み合わせます。
- 命名としては `orient` レベルの Action に相当します。
- 必要に応じて `attractiveness` や `stancebodyparam` を併用します。

### 手を対象へ差し出す

- `RightHandController` / `LeftHandController` に手先位置を与えます。
- BodyController を基準にする場合は `targetMotionMode=FromRobot(1)` や `transitionCoordinate=FromRobotSpine(5)` を使います。
- 指姿勢は `fingerData` で同時に指定します。
