# MiracleHuman の Motion・FACS・Action 機能別説明と定義方法

## 1. 概要

MiracleHuman では、身体動作・表情・複合行動を次の 3 段階で扱います。

| 種類 | 役割 | 代表コマンド |
|---|---|---|
| Motion | 手先・視線・体幹・関節角などの単体動作 | `playmotion`, `playthismotion`, `playthishandmotion`, `playthisanglemotion` |
| FACS | 表情 Action Unit / 表情プリセット | `setface`, `setmanualfacs`, `addfacs`, `blink` |
| Action | Motion / FACS / Controller / Attractiveness をツリー状に合成した行動 | `playaction`, `playthisaction`, `stopaction` |

## 2. 命名ルール

推奨される命名レベルは次の通りです。

| レベル | 単語 | モーションタイプ | 説明 |
|---|---|---|---|
| 部位だけ | `look` | `motion` | 目など単一部位の注視。 |
| 目 + 顔 | `gaze` | `action` | EyeController と HeadController の組み合わせ。 |
| 体含む | `orient` | `action` | Eye / Head / Body など全身方向づけ。 |

## 3. 定義済み Motion の再生

### playmotion

```text
playmotion=motionID\n
playmotion=motionA;motionB;\n
playmotion=motionA/0.1;motionB/10.0;\n
```

- `motionID` で定義済み Motion を再生します。
- `;` 区切りで複数指定できます。
- `/speedScale` を付けると速度スケールを指定できます。`0.1` はゆっくり、`10.0` は速い指定です。

### getmotions

```text
getmotions\n
```

返信:

```text
motionid;motionid;...;\n
```

## 4. Sequence Motion

複数の最小単位 Motion を、終了待ちや遅延を指定しながらシーケンシャルに実行します。

```text
playsequencemotion={"id":"right_hand_palmup_and_back","speedScale":1.0,"priority":0.0,"motionIDList":[{"id":"right_hand_byebye","startAfters":[],"startdelay":0,"speedScale":0.5},{"id":"right_hand_palmup","startAfters":["right_hand_byebye"],"speedScale":1.25,"startdelay":500}]}
```

主な項目:

| 項目 | 説明 |
|---|---|
| `id` | Sequence Motion の ID |
| `speedScale` | 全体速度スケール |
| `motionIDList` | 実行する Motion ノードの配列 |
| `startAfters` | 指定 Motion が全て終わったら開始 |
| `startdelay` | 開始前の待ち時間 `[msec]` |
| `priority` | 優先度 |

## 5. 未定義 Motion の動的生成

### playthismotion

Controller を動かす Motion JSON を送信し、動的に動作を生成します。

```text
playthismotion={"id":"right_hand_palmup_tmp","priority":0,"isRelative":false,"isGloablCoordinates":true,"motionPartName":"RightHandController","thoughSafetyStopoverPoint":false,"motionData":[{"id":"right_hand_palmup_tmp","motionTowardObject":"BodyController","targetMotionMode":1,"targetPoint":{"x":0,"y":0,"z":0.5},"translateSpeed":-1,"translateTime":850,"targetRotation":{"x":0,"y":90,"z":-90},"rotateSpeed":-1,"rotateTime":850,"keepTime":0,"mode":2,"gazeTracking":true,"priority":0,"tracking":true,"fingerData":[{"motionPartName":"RightIndexFinger","targetAngle":0,"springValue":10},{"motionPartName":"RightFingers","targetAngle":0,"springValue":10}]}]}
```

主な項目:

| 項目 | 説明 |
|---|---|
| `id` | Motion ID |
| `motionPartName` | 対象 Controller または Object |
| `motionData` | 時系列 MotionElement 配列 |
| `isRelative` | 相対指定かどうか |
| `isGloablCoordinates` | グローバル座標指定かどうか。既存表記に合わせて `Gloabl` の綴りを使う |
| `thoughSafetyStopoverPoint` | 安全な中継点を通すか |

### MotionElement

`motionData` 内の要素です。主なフィールドは次の通りです。

- `motionTowardObject`
- `targetMotionMode`
- `targetPoint`
- `translateSpeed` / `translateTime`
- `targetRotation`
- `rotateSpeed` / `rotateTime`
- `keepTime`
- `mode`
- `priority`
- `tracking`
- `fingerData`

## 6. HandMotion

### playthishandmotion

手の位置座標系と回転座標系を明示して、手先動作を定義します。

```text
playthishandmotion={"id":"left_hand_palmside_tmp","priority":0,"isRelative":false,"isGloablCoordinates":true,"motionPartName":"LeftHandController","thoughSafetyStopoverPoint":false,"motionHandData":[{"id":"left_hand_palmside_tmp","motionTowardObject":"BodyController","transitionCoordinate": 5,"targetPoint":{"x":0,"y":0,"z":0.5}, "targetPosOnObject": {"x": 0,"y": 0,"z": 0},"translateSpeed":-1,"translateTime":850,"rotationCoordinate": 7,"targetRotation":{"x":0,"y":0,"z":0},"keepTime":0,"priority":0,"tracking":true,"fingerData":[{"motionPartName":"LeftIndexFinger","targetAngle":0,"springValue":10},{"motionPartName":"LeftFingers","targetAngle":0,"springValue":10}]}]}
```

### transitionCoordinate

| 値 | 意味 |
|---:|---|
| 0 | `OnGlobal`: 世界座標系 |
| 1 | `OnRobot`: SpringMan 座標系 |
| 2 | `OnObject` |
| 3 | `FromObject` |
| 4 | `FromRobotHead` |
| 5 | `FromRobotSpine` |

### rotationCoordinate

| 値 | 意味 |
|---:|---|
| 0 | `PalmNaturalUpward` |
| 1 | `PalmNaturalDownward` |
| 2 | `PalmNaturalSide` |
| 3 | `PalmNaturalToward` |
| 4 | `PalmUpward` |
| 5 | `PalmDownward` |
| 6 | `PalmSide` |
| 7 | `PalmToward` |

### appendthishandmotion

```text
appendthishandmotion={handmotion json}\n
```

既存の HandMotion 定義に追加します。

## 7. AngleMotion

```text
playthisanglemotion=json\n
```

関節角度ベースの Motion です。腕 IK や体幹 IK で決定した関節角に対して、相対的にさらに各関節を曲げる用途に使います。頷きやビートモーションのような、相対動作の表現に適しています。

- `keepLast`: 最後の角度を保持します。

## 8. Motion 定義カテゴリ

### 座標定義ジェスチャ

手先の位置や視線など、対象座標を動的に動かすために使います。

- `Motion`
- `MotionOfHome`
- `MotionOfEyeGesture`
- `MotionOfHand`

### 関節角度ジェスチャ

- `AngleMotion`

## 9. FACS / 表情

### setface

```text
setface={"id":"FullSmile", "speedScale":1, "intensity":0.5}\n
setface={"id":"FullSmile", "speedScale":1, "intensity":0.5, "userSpecifyId":400}\n
```

- `id`: 表情 ID
- `speedScale`: `0.001`〜`10`。小さいほど遅く、大きいほど速い
- `intensity`: `0.001`〜`1`。小さいほど弱く、大きいほど強い。既定は `1`
- `userSpecifyId`: ControllerSync で返信と対応付けたい場合に使う任意 ID

### setmanualfacs

```text
setmanualfacs={"facsname":"MouthOpenClose", "value":1, "duration":1000}\n
```

- `facsname`: 操作する FACS パラメータ名
- `value`: `-1`〜`+1`
- `duration`: `>0` なら適用時間 `[msec]`、`0` 未満でその ActionUnit を使用しない

利用可能な代表パラメータ:

- `UpperLip`
- `LowerLip`
- `MouthOpenClose`
- `LipCornerPullDepressor_Right` / `LipCornerPullDepressor_Left`
- `MouthStickout`
- `LipStretch_Right` / `LipStretch_Left`
- `Cheek_Right` / `Cheek_Left`
- `InnerBrow`
- `LowerLid_Right` / `LowerLid_Left`
- `UpperLid_Right` / `UpperLid_Left`
- `OuterBrow_Right` / `OuterBrow_Left`
- `NoseWrinkler`

### addfacs

定義済み表情の FACS パラメータを上書きします。同じ表情がある場合は、`baseFACS` のパラメータと `TranslateTime` のみ上書きします。

```text
addfacs={"Id":"FullSmile","baseFACS":{"actionUnit":{"list":[{"Key":2,"Value":{"Value":1.0,"CPGScale":0.1}}]},"TranslateTime":1000, "blink":true}}\n
```

### Blink

```text
blink={"duration":500, "intentional":true}\n
blinkmodule={"enable":true}\n
```

- `duration`: 瞬き時間 `[msec]`
- `intentional`: `true` の場合、抑制されず上下瞬きになります。

## 10. Action

Action は Motion、Facial、Controller、Attractiveness、thismotion などをツリー状に組み合わせる機能です。

### 定義済み Action の再生

```text
playaction=string\n
```

### playthisaction

```text
playthisaction={
    "id":"attractive-byebye",
    "actionIDList":[{
        "action":{
            "actionType":"attractiveness",
            "attractiveProp":{
                "attractiveness":1.0,
                "transitionSpeed":-1.0,
                "transitionDuration":2000,
                "partName":"Body"
            }
        },
        "startdelay":0,
        "nextActions":[{
            "action":{
                "actionType":"motion",
                "predefinedActionName":"right_hand_byebye"
            },
            "startdelay":100,
            "speedScale":1.0,
            "intensity":1.0,
            "nextActions":[]
        }]
    },
    {"action":{
        "actionType":"facial",
        "predefinedActionName":"FullSmile"
    },
    "intensity":0.5,
    "startdelay":0
    }]
}\n
```

主な項目:

| 項目 | 説明 |
|---|---|
| `id` | Action ID |
| `destoryAfterFinish` | 終了後に破棄するか。既存表記に合わせて `destory` の綴りを使う |
| `actionIDList` | ルート Action ノード配列 |
| `action` | 実行する処理 |
| `startdelay` | 親開始後または条件成立後の遅延 `[msec]` |
| `speedScale` | Motion / Facial の速度スケール |
| `intensity` | Facial などの強度 |
| `nextActions` | この Action の後続として開始する Action ノード |

### actionType

| actionType | 用途 | 主な指定 |
|---|---|---|
| `motion` | 定義済み Motion 再生 | `predefinedActionName` |
| `facial` | 定義済み表情再生 | `predefinedActionName`, `intensity` |
| `attractiveness` | Head / Body / Stance の対象志向度変更 | `attractiveProp` |
| `controller` | Controller コマンド直接送信 | `thisCmd` |
| `thismotion` | JSON 内で Motion を直接定義 | `thisCmd` |

### stopaction

```text
stopaction={"id":123, "name":"action-name"}\n
```

- `id` または Action 名で停止対象を指定します。
- Action 名の場合、他の実行主体が開始した Action と一致する可能性があります。

## 11. ジェスチャ作成の注意

- オブジェクトからの相対でジェスチャを作る場合、向きは標準状態での向きを指定します。
- 位置指定には、オブジェクトのローカル座標系と、オブジェクトから見た顔の向き（Look）を `Z` 方向とした座標系があります。
- Greeting では Roll を `0` にすると、しゃきっとした動作になります。
