# MiracleHuman のシステム概要と使い方

## 1. システム概要

MiracleHuman は、Unity 上で構築されたヒューマノイド全身制御アプリケーションです。ヒューマノイドの身体は `ArticulationBody` を中心に構成され、外部アプリケーションから TCP コマンドを送信することで、視線・頭部・体幹・腕・手指・表情・内部状態・仮想オブジェクトなどを制御できます。

主な利用フローは次の通りです。

1. 起動時引数や UnityEditor の設定で、ロボット・環境・ロボット ID を選ぶ。
2. ControllerASync / ControllerSync / Streaming のいずれかの TCP ポートに接続する。
3. `EyeController=...`、`playmotion=...`、`setface=...`、`playaction=...` などのコマンドを送る。
4. 必要に応じて ControllerSync の完了通知や Streaming の状態配信を受け取る。

## 2. 起動


### 起動時にコマンドライン引数
ex) MiracleHuman.exe -selectrobot Erica -env ATREntrance -robotId handai
- "-selectrobot robotname"で自動でロボットを選ぶ
- "-localdebug"でAASSなど実機に送信しない
- "-env name"でScene.name.localdata.jsonを読み込んで設定を上書き，ロボットの位置やネットワーク情報など環境依存データの上書きに使用．
- "-robotid name"でScene.name.localdata.jsonを読み込んで設定を上書き，ロボットのAxisMapなどロボットのハードウェア依存データの上書きに使用．

## 3. 通信方式

MiracleHuman は用途の異なる 3 種類の TCP インターフェースを持ちます。

| 方式 | ポート | 用途 | 特徴 |
|---|---:|---|---|
| ControllerASync | 21000 | 通常の非同期コマンド送信 | 多くの制御コマンドをサポート。送信後すぐ次のコマンドを送れる。 |
| ControllerSync | 22000 | 完了通知が必要なコマンド送信 | 対応コマンドは限定されるが、start / finish / stop / failed などを受け取れる。 |
| Streaming | 9100 | 状態ストリーミング | ジョイント状態、メンタル状態、音声状態、Kinect 連携情報などを受信する。 |

> 注意: コマンドでは `=` の間にスペースを入れないでください。

## 4. ControllerASync の基本操作

### 4.1 Controller の直接移動

対象 Controller は主に次の 5 種類です。

- `EyeController`
- `HeadController`
- `BodyController`
- `RightHandController`
- `LeftHandController`

共通的な指定項目は次の通りです。

| 項目 | 説明 |
|---|---|
| `motionTowardObject` | 対象オブジェクト名。空文字なら `targetPoint` を直接使う。 |
| `targetMotionMode` | `FromObject(0)` / `FromRobot(1)` / `OnObject(2)`。 |
| `targetPoint` | 目標座標。ロボット座標系または対象に応じた座標。 |
| `translateSpeed` | 平行移動速度 `[m/sec]`。 |
| `translateAngularSpeed` | 注視方向などの角速度 `[deg/sec]`。 |
| `translateTime` | 移動時間 `[msec]`。`-1` の場合は速度指定を使う。 |
| `targetRotation` | 目標回転。 |
| `rotateSpeed` / `rotateTime` | 回転速度または回転時間。 |
| `tracking` | `true` の場合、対象を追従し続ける。 |
| `priority` | 優先度。視線などで反射的制御とゆっくりした追従を分ける用途。 |
| `mode` | `0:Lerp`、`1:Slerp`、既定は `Slerp`。 |

### 4.2 座標系

- ロボット正面: `z` 軸
- ロボット右方向: `x` 軸
- ロボット上方向: `y` 軸
- 原点: ロボットの腰の下付近
- 単位: メートル

### 4.3 ターゲット指定

人・ロボット・仮想オブジェクトを `motionTowardObject` で指定できます。

- Kinect などで生成される人の部位: `TargetHumanHead`、`TargetHumanSpine`、`TargetHumanRightHand`、`TargetHumanLeftHand` など
- ロボットの部位: `RightEye`、`LeftEye`、`Head`、`Spine`、`RightHand`、`LeftHand`
- 複数オブジェクト: `RightHand/LeftHand` のように `/` 区切り。`targetMotionMode=OnObject` なら重心を対象にできる。

## 5. 運用コマンド抜粋

以下はシステム運用に関係する代表的なコマンドです。Motion / FACS / Action の詳細は `MiracleHuman_Motion_FACS_Action.md`、制御モジュールの関係は `MiracleHuman_ArticulationBody_Modules.md` を参照してください。

### Attractiveness

```text
attractiveness={"partName":"Body", "attractiveness":1, "transitionDuration":1000}\n
```

- `partName`: `Head` / `Body` / `Stance`
- `attractiveness`: 対象に向ける度合い
- `transitionDuration`: 変化時間 `[msec]`
- `transitionSpeed`: 変化速度 `[/sec]`

### 内部状態

```text
arousal=float\n
valence=float\n
dominance=float\n
emotion={"dimension":"arousal", "value":1, "transitionDuration":1000}\n
```

### ターゲット Human / Robot の設定

```text
targethuman=4\n
subtargethuman=2\n
maintargetname=unique:4\n
subtargetname=N1H.test\n
```

### 再生中モーションの停止

```text
reset=all_playing_motions\n
```

### 仮想オブジェクト

```text
createobject={"id":"screen", "scale":{"x":1.6,"y":0.9,"z":0.2}, "position":{"x":0.0,"y":1.2,"z":-0.5}, "rotation":{"x":0,"y":0,"z":0}, "color":{"r":0,"g":5,"b":250,"a":128}, "isLookTarget":true, "isPointingTarget":true, "onObjectId":"", "tracking":false}
deleteobject={"id":"screen"}\n
```

### オブジェクト情報取得

```text
getobject=id\n
```

返信例:

```text
gotobject={"id":"name", "found": true, "globalposition":{"x":0,"y":0,"z":0}, "globalrotation":{"x":0,"y":0,"z":0,"w":0, "euler_x":0,"euler_y":0,"euler_z":0}}\n
```

### カメラ位置

```text
camera={"id": "Main Camera", "motionTowardObject": "", "targetMotionMode": 2, "targetPoint": {"x": 1.0,"y": 1.2,"z": 1.5}, "translateTime": 1000, "targetRotation": {"x":0.0,"y": -135.0,"z": 0.0}, "rotateTime": 1000}\n
```

### モーターコマンド送信制御

```text
sendmotorcmd=true\n
sendmotorcmd=false\n
```

## 6. ControllerSync

ControllerSync は非同期コマンドと同じ書式の一部コマンドを受け付け、処理開始・終了・停止・失敗の通知を返します。`userSpecifyId` をトップレベルに付けると、返信にも同じ ID が含まれます。

例:

```text
setface={"id":"FullSmile", "speedScale":1, "intensity":0.5, "userSpecifyId":400}\n
```

代表的な返信:

- Controller: `startcontroller` / `finishcontroller` / `stopcontroller`
- Gesture: `stargesture` / `finishgesture` / `stopgesture` / `failedgesture`
- Facial: `startfacial` / `finishfacial` / `failedfacial` / `alreadyfacial`
- Action: `startaction` / `finishaction` / `failedaction`
- Attractiveness: `startattractive` / `finishattractive` / `failedattractive` / `alreadyattractive`

## 7. Streaming

Streaming は 9100 port で状態を配信します。代表的な情報は次の通りです。

- `StateStreamer`: ジョイント状態、メンタル状態、音声状態
- `HumanLookingTowardRobot` / `HumanNotLookingTowardRobot`
- `HumanLookingTowardObject` / `HumanNotLookingTowardObject`
- `TargetHumanPointingObject` / `TargetHumanNotPointingObject`
- `UniquePeopleGazeObject`
- `UniquePeoplePointObject`
- `EyeContactState`
- `DangerousState` / `UniquePeopleDangerousState`
- `MentalState`
- `Warning` / `Error`

## 8. UnityEditor

`MainCamera/LocalEnvSetter` で環境名を入れることで、UnityEditor で起動する場合でも環境を設定できます。

## 9. その他

### カメラ平面の 3 次元プロジェクション

`SpringMan/EyeCameraController/CameraImage` では、画像上で向かって左が `X`、上が `Y` です。

---

# 付録: 旧 README から移設した全コマンドサンプル

この付録は、旧 `Release/docs/README.md` に掲載されていたコマンド例を削除せず参照できるように移設したものです。機能別の整理済み説明は本ファイルおよび `MiracleHuman_ArticulationBody_Modules.md`、`MiracleHuman_Motion_FACS_Action.md` を参照してください。


# 起動
## 起動時にコマンドライン引数
ex) MiracleHuman.exe -selectrobot Erica -env ATREntrance -robotId handai
- "-selectrobot robotname"で自動でロボットを選ぶ
- "-localdebug"でAASSなど実機に送信しない
- "-env name"でScene.name.localdata.jsonを読み込んで設定を上書き，ロボットの位置やネットワーク情報など環境依存データの上書きに使用．
- "-robotid name"でScene.name.localdata.jsonを読み込んで設定を上書き，ロボットのAxisMapなどロボットのハードウェア依存データの上書きに使用．


# コマンド

！注意！'='の間にスペースを入れてはならない
- 通信方式
  - ControllerASync
    本アプリがTCPサーバ（ port : 21000）で非同期通信を行う．コマンドのフッターは改行コード．文字コードはutf-8，
  - ControllerSync
    本アプリがTCPサーバ（ port : 22000）で同期通信を行う．
  - Streaming
    本アプリがTCPサーバ（ port : 9100）で非同期通信を行う．状態がストリーミングされる．



## RontrollerASync 送信コマンド

### Controllerの移動コマンド
- MotionController部位
   - EyeController
   - HeadController
   - BodyController
   - RightHandController
   - LeftHandController
- MotionController部位はMotionElementを指定する　mode:0 Lerp, 1:Slerp, default:Slerp
- x,y,zで視線，顔，体を向ける座標を指定する
- ロボットの正面方向がz軸，右がx軸，上がy軸の左手座標系でロボットの腰の下が原点，単位はメートル，translateSpeed(移動速度)は[m/sec], translateAngularSpeed[deg/sec]
  priorityはfloatでデフォルトは0
  反射的に視線を向ける場合とゆっくりトラッキングする場合とでpriorityを変えると吉
- motionTowardObjectで対象となるオブジェクトを指定する
  - センサーで作られるK2BodyのObjectを使う場合（MimicGestureを作る場合や人の顔を向ける）
    - TargetHumanかSubTargetHumanに加え対象部位HeadとかSpineとかRightHandとかLeftHandをオブジェクト名にする, ただしmaintargetname, subtargetnameでロボットを指定した場合はそのロボットが対象となる
      - 例：```TargetHumanHead```とか
    - Robotの部位 ```RightEye```, ```LeftEye```, ```Head```, ```Spine```, ```RightHand```, ```LeftHand```を対象にする場合はRobot名に部位をくっつけて指定, ロボット名は```Robotシーン名.環境名```
      - 例：```N1LHead```とか
      - 環境名も加味すると ```N1H.CafeHead```, ```CafeHead```と環境名だけ指定しても一応対応できるが環境名を互いに含まないように切り分けることを勧める．マッチングはStartｓWith
  - RightHand/LeftHandのように/で複数のオブジェクトを指定し，OnObjectにすると複数のオブジェクトの重心を見ることができる/で区切れば3個以上も多分対応．
- targetMotionMode=FromObject(0),FromRobot(1),OnObject(2)
- EyeControllerについてpriority>=2だとblinkが連動する

```
RightHandController={"id": "RightHandController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 1.5},"translateSpeed": 1.0,"translateTime": -1,"translateAngularSpeed": -1,"targetRotation": {"x":0.0,"y": 0.0,"z": 0.0},"rotateSpeed": 270,"rotateTime": -1,"keepTime": 0,"mode": 2,"gazeTracking": true,"priority": 0,"isBezierCurvePoint": false,"fingerData": []}\n
```
#### EyeController, HeadController, BodyController
##### 視線は角速度指定のほうがいい，距離が離れると平行移動速度が上がる，translateSpeedで制御しちゃうと手前のものほど首の振りが速くなってしまう
```
EyeController={"id": "EyeController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 1.0},"translateAngularSpeed": 90.0, "tracking":false}
HeadController={"id": "HeadController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 1.0},"translateAngularSpeed": 90.0, "tracking":false}
BodyController={"id": "BodyController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 1.0},"translateAngularSpeed": 90.0, "tracking":false}
HeadController={"id": "HeadController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 1.0},"translateAngularSpeed": 90.0, "tracking":false}
HeadController={"id": "HeadController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 1.0,"y": 1.2,"z": 0},"translateAngularSpeed": 90.0, "tracking":false}
HeadController={"id": "HeadController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 2.5},"translateAngularSpeed": 90.0, "tracking":false}
HeadController={"id": "HeadController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 2.5,"y": 1.2,"z": 0},"translateAngularSpeed": 90.0, "tracking":false}
HeadController={"id": "HeadController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 5.0},"translateAngularSpeed": 90.0, "tracking":false}
HeadController={"id": "HeadController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 5.0,"y": 1.2,"z": 0},"translateAngularSpeed": 90.0, "tracking":false}
```

#### priorityが2以上のEyeController制御は瞬きが連動する，これは意識的に対象に視線を向ける瞬間という制御
```
EyeController={"id": "EyeController","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 1.0,"y": 1.2,"z": 1.0},"translateAngularSpeed": 90.0, "priority":2}
```
##### 見続ける，手を添え続けるには"tracking": true
```
HeadController={"id": "HeadController","motionTowardObject": "monitor","tracking": true, "targetMotionMode": 2,"targetPoint": {"x":0,"y": 0,"z": 0},"translateSpeed": 2.0}\n
```
- 左手をみつづける Enumは0スタート, From Object = 0, Toward Object = 1, On Object = 2
```
EyeController={"id": "EyeController","motionTowardObject": "LeftHand","targetMotionMode": 2,"tracking": true,"targetPoint": {"x": 0,"y": 0,"z": 0},"translateSpeed": 2.0,"translateTime": -1,"targetRotation": {"x": 0.0,"y": 0.0,"z": 0.0},"rotateSpeed": 270,"rotateTime": -1,"keepTime": 0,"mode": 2,"gazeTracking": true,"priority": 0,"isBezierCurvePoint": false,"fingerData": []}\n
```
- 体の右前
```
EyeController={"id": "EyeController","motionTowardObject": "Spine","targetMotionMode": 2,"tracking": true,"targetPoint": {"x": 1,"y": 1,"z": 1},"translateSpeed": 2.0,"translateTime": -1,"targetRotation": {"x": 0.0,"y": 0.0,"z": 0.0},"rotateSpeed": 270,"rotateTime": -1,"keepTime": 0,"mode": 2,"gazeTracking": true,"priority": 0,"isBezierCurvePoint": false,"fingerData": []}
```

- ターゲットの頭を見る（ターゲットとなるのはunique idを持つ人かロボット）
```
EyeController={"id": "EyeController","motionTowardObject": "TargetHumanHead","targetMotionMode": 2,"tracking": false,"targetPoint": {"x": 0,"y": 0,"z": 0},"translateAngularSpeed": 90.0,"mode": 2,"priority": 0}
```


- mode:0 Lerp, 1:Slerp, default:Slerp
```
EyeController={"id": "EyeController","motionTowardObject": "Spine","mode":0, "targetMotionMode": 2,"tracking": true,"targetPoint": {"x": 1,"y": 1,"z": 1},"translateSpeed": 2.0,"translateTime": -1,"targetRotation": {"x": 0.0,"y": 0.0,"z": 0.0},"rotateSpeed": 270,"rotateTime": -1,"keepTime": 0,"mode": 2,"gazeTracking": true,"priority": 0,"isBezierCurvePoint": false,"fingerData": []}
```
## Attractiveness(HeadController, BodyController)
- attractiveness={"partName":"Head/Body/Stance", "attractiveness":float, "transitionDuration":int, "transitionSpeed":float}\n
```
attractiveness={"partName":"Body", "attractiveness":1, "transitionDuration":1000}\n
```
- transitionSpeed: 変化速度[/sec]
- transitionDuration: 変化時間[msec]どちらかを指定すると線形でその時間かけて変化する，急激な変化を避けられる

↓古い非推奨
※Attractivenessの要素も追加できる
顔，体を向ける度合いを指定する(対象からそらす：-1.0~+1.0：対象に向ける)
BodyController={"attractiveness":0.5}\n
HeadController={"attractiveness":-0.5}\n
フルコマンド: transitionSpeedは変化速度[/sec]，transitionDurationは変化時間[msec]どちらかを指定すると線形でその時間かけて変化する，急激な変化を避けられる
{"attractiveness":-0.5, "transitionSpeed":0.1, "transitionDuration":5000}\n
BodyController={"attractiveness":1.0, "transitionDuration":5000}\n
HeadController={"attractiveness":-1.0, "transitionSpeed":1.0}\n

### 眼球スペシャルコマンド
- gazeavert
  - float scale is degree, change automatically EyeController position, pitch_degree > 0 downward, <0 upward
  - angularSpeed[deg/sec]
```
gazeavert={"pitch_degree":0.0, "yaw_degree":0.0, "angularSpeed": 180.0}\n
gazeavert={"pitch_degree":10.0, "yaw_degree":10.0, "angularSpeed": 180.0}\n
```

- サッケード
  サッケードを自動でするかしないか
```
  saccade=true/false\n
```

### ジェスチャ再生
#### 命名ルール（推奨であって必須じゃない）

#### 注視
--------------------
| レベル|	単語	|モーションタイプ|
|---|---|---|
|部位だけ|look|motion|
|目＋顔| gaze |action|
|体含む| orient |action|

#### 定義済みジェスチャの再生
- playmotion=motionID\n
  - playmotion=motionA;...;motionB;\n
  - 動きの速度をスケーリングするオプション，0.1（ゆっくり）~10.0（早い）
  - playmotion=motionA/0.1;...;motionB/10.0;\n

- getmotions\n -> motionid;motionid;.....;\n
- playsequencemotion
  シーケンシャルに動作をプレイ．手を差し出してちょっとしたら戻すって感じ．
  - speedScaleはシーケンシャルに呼び出す動作すべてをスケーリングする
  - startAftersリストのモーションが全て終わったらidで指定するモーションを再生する，ただしここで指定できるモーションはhandmotion, anglemotionなど最小単位モーションのみ
  - startdelayはstartAftersのモーションが終わってからstartAfters[msec]まって次の動作を開始する
  - speedScaleはモーション全体をスケーリングするのと，各モーションを相対的にスピードをスケーリングする2要素がある
```
playsequencemotion={"id":"right_hand_palmup_and_back","speedScale":1.0,"priority":0.0,"motionIDList":[{"id":"right_hand_byebye","startAfters":[],"startdelay":0,"speedScale":0.5},{"id":"right_hand_palmup","startAfters":["right_hand_byebye"],"speedScale":1.25,"startdelay":500}]}
```

#### 未定義動作生成
- playthismotion={motion json}\n
  Controllerを動かすモーションJsonを送りつけて動的にPathも含め動作生成する
  - (right palm up body controller)
```
playthismotion={"id":"right_hand_palmup_tmp","priority":0,"isRelative":false,"isGloablCoordinates":true,"motionPartName":"RightHandController","thoughSafetyStopoverPoint":false,"motionData":[{"id":"right_hand_palmup_tmp","motionTowardObject":"BodyController","targetMotionMode":1,"targetPoint":{"x":0,"y":0,"z":0.5},"translateSpeed":-1,"translateTime":850,"targetRotation":{"x":0,"y":90,"z":-90},"rotateSpeed":-1,"rotateTime":850,"keepTime":0,"mode":2,"gazeTracking":true,"priority":0,"tracking":true,"fingerData":[{"motionPartName":"RightIndexFinger","targetAngle":0,"springValue":10},{"motionPartName":"RightFingers","targetAngle":0,"springValue":10}]}]}
```

#### 未定義手動作生成
- playthishandmotion={handmotion json}\n
  - transitionCoordinate: OnGlobal(0)世界座標系, OnRobot(1)SpringMan座標系, OnObject(2), FromObject(3), FromRobotHead(4), FromRobotSpine(5)
  - rotationCoordinate: PalmNaturalUpward(0)//回転座標系で手のひらを上Y+方向, PalmNaturalDownward(1)//回転座標系で手のひらを下Y-方向, PalmNaturalSide(2)//回転座標系で手のひらを水平体の中心方向, PalmNaturalToward(3)//手のひらを対象方向Z+, PalmUpward(4)//回転座標系で手のひらを上Y+方向, PalmDownward(5)//回転座標系で手のひらを下Y-方向, PalmSide(6)//回転座標系で手のひらを水平体の中心方向, PalmToward(7)//手のひらを対象方向Z+
  - motionDirectionTowardObject: motionTowardObjectは座標を決めるためで，もしその位置から別の対象に手を向ける場合にはこれで対象を指定する
  - K2BodyのObjectを使う場合（MimicGestureを作る場合）
    - TargetHuman/SubTargetHuman+Head/Spine/RightHand/LeftHand
  - (left hand shake body controller)
```
playthishandmotion={"id":"left_hand_palmside_tmp","priority":0,"isRelative":false,"isGloablCoordinates":true,"motionPartName":"LeftHandController","thoughSafetyStopoverPoint":false,"motionHandData":[{"id":"left_hand_palmside_tmp","motionTowardObject":"BodyController","transitionCoordinate": 5,"targetPoint":{"x":0,"y":0,"z":0.5}, "targetPosOnObject": {"x": 0,"y": 0,"z": 0},"translateSpeed":-1,"translateTime":850,"rotationCoordinate": 7,"targetRotation":{"x":0,"y":0,"z":0},"keepTime":0,"priority":0,"tracking":true,"fingerData":[{"motionPartName":"LeftIndexFinger","targetAngle":0,"springValue":10},{"motionPartName":"LeftFingers","targetAngle":0,"springValue":10}]}]}
```

- appendthishandmotion={handmotion json}\n

#### 未定義角度動作作生成
playthisanglemotion=json\n

### ジェスチャの定義
#### 座標定義ジェスチャ
手先の位置や視線など注視対称座標を動的に動かすのに使用．
- Motion
- MotionOfHome
- MotionOfEyeGesture
- MotionOfHand

#### 関節角度ジェスチャ
腕IKや体幹IKモジュールで決定した関節角度に相対的に更に各関節を曲げる．頷きやビートモーションなど相対的動きのあるジェスチャで使用．
- AngleMotion
  - keepLast : 最後の角度を保持

### 体幹制御手動設定
- trunkjointparam={"part":"SpineYaw", "useManual":true,"angle":40.0, "smoothingSpeed":45.0}\n
  - part : SpineYaw/SpinePitch
  - useManual : falseで自動計算に戻る
  - angle : 基準からの絶対角度，範囲以上を指定した場合は最大可動範囲内に制限される
  - smoothingSpeed : はdeg/secで-1にすればデフォルト値


### 下半身とBodyControllerの連動設定
- stancebodyparam={"part":"Pitch", "ratio":0.5}\n
  - part : Yaw/Pitch, 連動軸
  - ratio : 0.0~1.0, 1に近いほど下半身がBodyController方向を向く，またBodyControllerのAttractiveにも連動し前傾にもなる

### ターゲットHumanのIDの設定
- targethuman=4\n
- subtargethuman=2\n

### ターゲットをロボット人問わずに設定
- コマンド
  - maintargetname=id\n
  - subtargetname=id\n
- idルール
  - 人の場合 unique:int, ex: unique:4
  - ロボットの場合 scenename.envname, ex: N1H.test, envnameを指定しなくてもいいがもし同じ型番が同じ空間上にいる場合は正しいほうが選ばれる保証はない


### play中のモーションなどを停止する
- コマンド
  - reset=all_playing_motions\n



### マニュアルでロール姿勢を変えるコマンド，これを送れば自動でEmotion2Poseは止まる
- rollpose={"degree":float, "direction":"left/right", "samedirection":true/false, "rollspeed":float}\n
  - rollpose={"degree":5.0, "direction":"left", "samedirection":true, "rollspeed":20.0}\n
  - rollspeedを指定しないとデフォルトの速度になる[deg/sec]

### Emotion2Poseを再開・停止
- modulecontrol={"moduleName":"Emotion2Pose", "permit": true/false}\n

### Central pattern generator
- cpg={"scale":float>=0, "frequency":float>=0, "perlinscale":float>=0}\n
  - cpg={"scale":5, "frequency":2, "perlinscale":1}\n
  - scale 0(small)~2.5(default)~5(large)
  - frequency 0(slow)~0.15(default)~0.3(fast)
  - perlin noise scale 0(small)~1(large,default)

### 内部状態の設定
#### 単純
- arousal=float\n
- valence=float\n
- dominance=float\n

#### 時間，速度指定
- emotion={"dimension":"arousal/valence/dominance", "value":float, "transitionDuration":int[msec], "transitionSpeed":float[value/sec]}\n
```
emotion={"dimension":"arousal", "value":1, "transitionDuration":1000}\n
```
```
emotion={"dimension":"valence", "value":1, "transitionSpeed":0.5}\n
```


### Listening Behavior
対話相手のセンシングに合わせて頷きなどを自動生成
- 設定jsonファイルのノードListeningProsodyで話者の声を解析したCoeCoreに接続する必要がある
- 首で頷き角度が十分確保できないと首も動かす

ONOFFコマンド
- listeningmodule={"enable":true/false}\n

### 表情指定
- setface={"id":string, "speedScale":float, "intensity":float}\n
  - speedScale: 0.001 ~ 10, <-> slow ~ fast
  - intensity: 0.001 ~ 1 <-> small ~ big, default 1
    - setface={"id":"FullSmile", "speedScale":1, "intensity":0.5}\n
    - setface={"id":"FullSmile", "speedScale":1, "intensity":0.5, "userSpecifyId":400}\n

##### ManualFACSパラメータ指定
- setmanualfacs={"facsname":string, "value":float, "duration":int}\n
  - facsname:UpperLip, LowerLip, MouthOpenClose, LipCornerPullDepressor_Right, LipCornerPullDepressor_Left, MouthStickout, LipStretch_Right, LipStretch_Left, Cheek_Right, Cheek_Left, InnerBrow, LowerLid_Right, LowerLid_Left, UpperLid_Right, UpperLid_Left, OuterBrow_Right, OuterBrow_Left, NoseWrinkler
  - value:-1~+1
  - duration:>0[msec],  0<でそのActionUnitを使用しなくする
  - setmanualfacs={"facsname":"MouthOpenClose", "value":1, "duration":1000}

##### FACS表情パラメータ上書き
- addfacs=json\n
  - 同じ表情がある場合はbaseFACSのパラメータとTranslateTimeのみ上書き
  - 例　FullSmileを口開ける
  - addfacs={"Id":"FullSmile","baseFACS":{"actionUnit":{"list":[{"Key":2,"Value":{"Value":1.0,"CPGScale":0.1}}]},"TranslateTime":1000, "blink":true}}\n

#### Blink
任意のタイミングで瞬き
- blink={"duration":int, "intentional":bool}\n
  - duration:msec
  - intentional:true/false trueだったら抑制されず上下瞬き
  - blink={"duration":500, "intentional":true}

瞬きのONOFF
- blinkmodule={"enable":true/false}\n



### action
- playaction=string\n
- playthisaction=json\n
```
playthisaction={"id":"actiontest2","destoryAfterFinish":true, "actionIDList":[{"action":{"actionType":"motion","predefinedActionName":"greeting"},"startdelay":0,"speedScale":1.0,"nextActions":[{"action":{"actionType":"facial","predefinedActionName":"FullSmile"},"startdelay":100,"speedScale":1.0,"nextActions":[]},{"action":{"actionType":"motion","predefinedActionName":"right_hand_byebye"},"startdelay":500,"speedScale":1.0,"nextActions":[]}]}]}
playthisaction={"id":"actiontest","actionIDList":[{"action":{"actionType":"motion","predefinedActionName":"greeting","thisCmd":"{}","attractiveProp":{"attractiveness":0.5,"transitionSpeed":-1.0,"transitionDuration":-1,"partName":""}},"startdelay":0,"speedScale":1.0,"intensity":1.0,"nextActions":[{"action":{"actionType":"facial","predefinedActionName":"FullSmile","thisCmd":"{}","attractiveProp":{"attractiveness":0.5,"transitionSpeed":-1.0,"transitionDuration":-1,"partName":""}},"startdelay":100,"speedScale":1.0,"intensity":1.0,"nextActions":[]},{"action":{"actionType":"motion","predefinedActionName":"right_hand_byebye","thisCmd":"{}","attractiveProp":{"attractiveness":0.5,"transitionSpeed":-1.0,"transitionDuration":-1,"partName":""}},"startdelay":500,"speedScale":1.0,"intensity":1.0,"nextActions":[{"action":{"actionType":"attractiveness","predefinedActionName":"attractiveness=1","thisCmd":"","attractiveProp":{"attractiveness":1.0,"transitionSpeed":-1.0,"transitionDuration":1000,"partName":"Body"}},"startdelay":0,"speedScale":1.0,"intensity":1.0,"nextActions":[{"action":{"actionType":"thismotion","predefinedActionName":"motion","thisCmd":"{\"id\":\"right_hand_palmup_tmp\",\"priority\":0,\"isRelative\":false,\"isGloablCoordinates\":true,\"motionPartName\":\"RightHandController\",\"thoughSafetyStopoverPoint\":false,\"motionData\":[{\"predefinedActionName\":\"right_hand_palmup_tmp\",\"motionTowardObject\":\"BodyController\",\"targetMotionMode\":1,\"targetPoint\":{\"x\":0,\"y\":0,\"z\":0.5},\"translateSpeed\":-1,\"translateTime\":850,\"targetRotation\":{\"x\":0,\"y\":90,\"z\":-90},\"rotateSpeed\":-1,\"rotateTime\":850,\"keepTime\":0,\"mode\":2,\"gazeTracking\":true,\"priority\":0,\"tracking\":true,\"fingerData\":[{\"motionPartName\":\"RightIndexFinger\",\"targetAngle\":0,\"springValue\":10},{\"motionPartName\":\"RightFingers\",\"targetAngle\":0,\"springValue\":10}]}]}","attractiveProp":{"attractiveness":0.5,"transitionSpeed":-1.0,"transitionDuration":-1,"partName":""}},"startdelay":100,"speedScale":1.0,"intensity":1.0,"nextActions":[{"action":{"actionType":"attractiveness","predefinedActionName":"attractiveness=0","thisCmd":"","attractiveProp":{"attractiveness":0.0,"transitionSpeed":0.0,"transitionDuration":500,"partName":"Body"}},"startdelay":0,"speedScale":1.0,"intensity":1.0,"nextActions":[]}]}]}]}]}],"destoryAfterFinish":false}\n
```
```
playthisaction={"id":"attractive-byebye","actionIDList":[{"action":{"actionType":"attractiveness","attractiveProp":{"attractiveness":1.0,"transitionSpeed":-1.0,"transitionDuration":2000,"partName":"Body"}},"startdelay":0,"nextActions":[{"action":{"actionType":"motion","predefinedActionName":"right_hand_byebye"},"startdelay":100,"speedScale":1.0,"intensity":1.0,"nextActions":[]}]},{"action":{"actionType":"facial","predefinedActionName":"FullSmile"},"intensity":0.5,"startdelay":0}]}\n
```

  - 横見て笑ってお辞儀
```
playthisaction={"id":"hospitality-greeting","actionIDList":[{"action":{"actionType":"controller","predefinedActionName":"","thisCmd":"{\"id\":\"EyeController\",\"priority\":2,\"targetMotionMode\":2,\"targetPoint\":{\"x\":1.0,\"y\":1.5,\"z\":2.0},\"translateAngularSpeed\":90.0}"},"startdelay":0,"speedScale":1.0,"intensity":1.0,"nextActions":[]},{"action":{"actionType":"controller","predefinedActionName":"","thisCmd":"{\"id\":\"HeadController\",\"targetMotionMode\":2,\"targetPoint\":{\"x\":1.0,\"y\":1.5,\"z\":2.0},\"translateAngularSpeed\":40.0}"},"startdelay":0,"speedScale":1.0,"intensity":1.0,"nextActions":[]},{"action":{"actionType":"controller","predefinedActionName":"","thisCmd":"{\"id\":\"BodyController\",\"targetMotionMode\":2,\"targetPoint\":{\"x\":1.0,\"y\":1.5,\"z\":2.0},\"translateAngularSpeed\":30.0}"},"startdelay":0,"speedScale":1.0,"intensity":1.0,"nextActions":[{"action":{"actionType":"facial","predefinedActionName":"FullSmile","thisCmd":"{}"},"startdelay":200,"speedScale":1.0,"intensity":1.0,"nextActions":[{"action":{"actionType":"motion","predefinedActionName":"greeting","thisCmd":""},"startdelay":0,"speedScale":1.0,"intensity":1.0,"nextActions":[{"action":{"actionType":"facial","predefinedActionName":"MoodBasedFACS","thisCmd":""},"startdelay":200,"speedScale":1.0,"intensity":1.0,"nextActions":[]}]}]}]}],"destoryAfterFinish":false}
```
- stopaction={"id":long, "name":string}\n
  - idかアクション名で指定，アクション名の場合は誰かが実行したアクションの可能性もある

### 角度指定(デフォルトの姿勢を変える)
- sethingejoint={"part":"objectname", "angle":double}\n
- setconfigjoint={"part":"objectname", "angle":{"x":-1.0,"y":-0.5,"z":3.5}}\n
- setarticulationbodyjoint={"part":"objectname", "angle":{"x":-1.0,"y":-0.5,"z":3.5}}\n

### axis valueにオフセットを加える
- offset={"axis":int, "value":int}\n
- offset={"axis":2, "value":-20}\n

### モジュールのONOFF
- modulecontrol={"moduleName":"name", "permit": true/false}\n
  - ex;
  - modulecontrol={"moduleName":"Emotion2Pose", "permit": true/false}\n

### 仮想オブジェクトの追加削除
- 位置・回転はGlobal
  - createobject={"id":"screen", "scale":{"x":1.6,"y":0.9,"z":0.2}, "position":{"x":0.0,"y":1.2,"z":-0.5}, "rotation":{"x":0,"y":0,"z":0}, "color":{"r":0,"g":5,"b":250,"a":128}, "isLookTarget":true, "isPointingTarget":true, "onObjectId":"", "tracking":false}
  - deleteobject={"id":"name"}\n
  - objectはCube一個で，isLookTarget=trueにすると人が見ているものの判定に含まれる，isPointingTarget=trueにすると人が指差しているものの判定に含まれる
  - objectはmotion定義で動かすことができる
    - playthismotion={"id":"screen_move","motionPartName":"screen","motionData":[{"id":"0","targetPoint":{"x":0,"y":2,"z":2},"translateSpeed":-1,"translateTime":1000,"targetRotation":{"x":0,"y":90,"z":-90},"rotateSpeed":-1,"rotateTime":-1,"keepTime":0,"mode":2}, {"id":"1","targetPoint":{"x":0,"y":1,"z":-0.5},"translateSpeed":-1,"translateTime":1000,"targetRotation":{"x":0,"y":0,"z":0},"rotateSpeed":-1,"rotateTime":-1,"keepTime":0,"mode":2}]}

#### オブジェクトの情報取得
- getobject=id\n
->gotobject={"id":"name", "found": true/false, "globalposition":{"x":0,"y":0,"z":0}, "globalrotation":{"x":0,"y":0,"z":0,"w":0, "euler_x":0,"euler_y":0,"euler_z":0}}\n

### カメラ位置の変更
Motionと同じパラメータだけど使えないパラメータは指定しないこと
- camera={"id": "Main Camera","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 0.0,"y": 1.2,"z": 1.5},"translateSpeed": 1.0,"translateTime": -1,"targetRotation": {"x":0.0,"y": 0.0,"z": 0.0},"rotateSpeed": 270,"rotateTime": -1,"keepTime": 0,"mode": 2,"}\n
- camera={"id": "Main Camera","motionTowardObject": "","targetMotionMode": 2,"targetPoint": {"x": 1.0,"y": 1.2,"z": 1.5},"translateTime": 1000, "targetRotation": {"x":0.0,"y": -135.0,"z": 0.0},"rotateTime": 1000}\n

### モーターコマンド送信制御
- sendmotorcmd=true/false\n

## RontrollerSync 送信コマンド
送信コマンドに対し返事を待つ送信コマンドは非同期と同じだがサポートしているコマンドが限られている
同期通信コマンドに"userSpecifyId":long>=0を最初のレベルに加えるとそれも返事に入れてくれる
userSpecifyIdを指定すると返信にもuserSpecifyIdが含まれる
- setface={"id":"FullSmile", "speedScale":1, "intensity":0.5, "userSpecifyId":400}\n

### controllerの位置
- EyeController, HeadControoler, BodyController, RightHandController, LeftHandController
  →startcontroller={"name":"EyeController", "id":long}\n
  →finishcontroller={"name":"EyeController", "id":long}\n
  →stopcontroller={"name":"EyeController", "id":long}\n
  idはplayしたときに

### gestureの再生
- playmotion,playsequencemotion,playthismotion,playthishandmotion,playthisanglemotion
  →stargesture={"name":"greeting", "id":long}\n
  →finishgesture={"name":"greeting", "id":long}\n
  →stopgesture={"name":"greeting", "id":long}\n
  →failedgesture={"name":"greeting"}\n

### 視線反らし
- gazeavert
  →startgazeavert={"name":"GazeAvert", "id":long}\n
  →finishgazeavert={"name":"GazeAvert", "id":long}\n
  →stopgazeavert={"name":"GazeAvert", "id":long}\n


### facial
- setface
  →finishfacial={"name":string, "id":long}\n
  →startfacial={"name":string, "id":long}\n
  →failedfacial={"name":string}\n
  →alreadyfacial={"name":string}\n

### action
- playaction, playthisaction
  →startaction={"name":"greeting", "id":long}\n
  →finishaction={"name":"greeting", "id":long}\n
  →failedaction={"name":"greeting"}\n

### attractiveness
- attractiveness
  →startattractive={"partName":"Body/Head/Stance","attractiveness":float, "id":long}\n
  →finishattractive={"partName":"Body/Head/Stance","attractiveness":float, "id":long}\n
  →failedattractive={"partName":"Body/Head/Stance","attractiveness":float}\n
  →alreadyattractive={"partName":"Body/Head/Stance","attractiveness":float}\n

### オブジェクトの情報取得
- getobject=id\n
  ->gotobject={"id":"name", "found": true/false, "globalposition":{"x":0,"y":0,"z":0}, "globalrotation":{"x":0,"y":0,"z":0,"w":0, "euler_x":0,"euler_y":0,"euler_z":0}}\n


## Streamingの受信コマンド 9100port
### ジョイント情報
- StateStreamer = {json}
例
```
StateStreamer={"jointstate":[{"jointname":"BodyBase_Joint", "jointdata":{"xAngle":0.001181164, "yAngle":-0.0001736546, "zAngle":-0.2352905,"globalposition":{"x":-0.01299152, "y":0.982211, "z":-4.925423E-06},"globalrotation":{"x":1.030132E-05, "y":-1.633156E-06, "z":-0.002053368, "w":0.999998, "euler_x":0.001180058, "euler_y":-0.0001895694, "euler_z":359.7647}},"bodydata":{"bodyname":"BodyBase","globalposition":{"x":-0.01299152, "y":0.982211, "z":-4.925423E-06},"globalrotation":{"x":1.030132E-05, "y":-1.633156E-06, "z":-0.002053368, "w":0.999998},"scale":{"x":-1, "y":-1, "z":-1}}}], "mentalstate":{"arousal":0, "valence":0, "dominance":0, "smoothed_arousal":0, "smoothed_valence":0, "smoothed_dominance":0}, "speechstate":{"bestviseme":"sil","laughterScore":0.008914289996027947,"sil":1.0,"PP":0.0,"FF":0.0,"TH":0.0,"DD":0.0,"kk":0.0,"CH":0.0,"SS":0.0,"nn":0.0,"RR":0.0,"aa":0.0,"E":0.0,"ih":0.0,"oh":0.0,"ou":0.0,"prosodyInfo":{"power":0.0,"f0Hz":152.0,"intonation":"FALL","semitioneDiff":-14.072174072265625,"intonationDuration":-480,"speechFeature":"FALLDOWN","beat":false,"powerDiffAtBeat":7.269073486328125}}}
```

#### jointstate
- json array
 {"jointname":string,"jointdata":{"xAngle":float,"yAngle":float,"zAngle":float,"globalposition":{"x":float,"y":float,"z":float},"globalrotation":{"x":float,"y":float,"z":float,"w":float,"euler_x":float,"euler_y":float,"euler_z":float}}}
  - xAngle, yAngle, zAngleは関節初期姿勢からの相対的角度状態
  - globalposition，globalrotationは関節の世界座標での位置と回転
  - 例
```
    {"jointstate":[{"jointname":"Pelvis","jointdata":{"xAngle":-0.0002924751,"yAngle":-0.001763284,"zAngle":-0.0001642044,"globalposition":{"x":7.479929E-06,"y":0.4644818,"z":0.000134584},"globalrotation":{"x":1.526551E-05,"y":-1.974715E-06,"z":-1.507928E-06,"w":1,"euler_x":0.001749299,"euler_y":-0.0002262883,"euler_z":-0.0001727993}}}]}
```
#### mentalstate
- "mentalstate":{"arousal":0, "valence":0, "dominance":0, "smoothed_arousal":0, "smoothed_valence":0, "smoothed_dominance":0},

#### speechstate
-LipSyncのJsonまんま
```
"speechstate":{"bestviseme":"sil","laughterScore":0.008914289996027947,"sil":1.0,"PP":0.0,"FF":0.0,"TH":0.0,"DD":0.0,"kk":0.0,"CH":0.0,"SS":0.0,"nn":0.0,"RR":0.0,"aa":0.0,"E":0.0,"ih":0.0,"oh":0.0,"ou":0.0,"prosodyInfo":{"power":0.0,"f0Hz":152.0,"intonation":"FALL","semitioneDiff":-14.072174072265625,"intonationDuration":-480,"speechFeature":"FALLDOWN","beat":false,"powerDiffAtBeat":7.269073486328125}}}
```
### Kinectの情報と組み合わせたときのみ
#### ユーザの視線情報 SpringManはロボットを指す
- TargetHumanのロボットに対しての視線情報
  - HumanLookingTowardRobot={\"x\":" +float+",\"y\":" + float + ",\"z\":" + float+ ",\"layer2_x\":" + float + ",\"layer2_y\":" + float + ",\"layer2_z\":" + float+ "}\n");
  - HumanNotLookingTowardRobot\n
- その他ものに対しての視線情報
  - HumanLookingTowardObject={\"x\":" + float + ",\"y\":" + float + ",\"z\":" + float + ",\"layer2_x\":" + float + ",\"layer2_y\":" + float + ",\"layer2_z\":" + float + ",\"objectname\":" + "\""+string+ ",\"objectdetailedname\":" + "\""+string+ "\"" + "}\n"
  - HumanNotLookingTowardObject\n
- TargetHumanの指差し情報（SpringManとオブジェクトすべて対象）
```
TargetHumanPointingObject={\"x\":" + float + ",\"y\":" + float + ",\"z\":" + float + ",\"layer2_x\":" + float + ",\"layer2_y\":" + float + ",\"layer2_z\":" + float + ",\"objectname\":" + "\""+string+ ",\"objectdetailedname\":" + "\""+string+ "\"" + "}\n"
```
- TargetHumanNotPointingObject\n
- ユニークIDがついている人が見ている情報(見ていないとnone)+lookdetailedatはより詳細な部位
  - UniquePeopleGazeObject={\"uniquepeoplegazeobject\":[{"hid":4, "islooking":true, "looking":[{},{}...]},{"hid":3, "islooking":false}]}\n
    - id:名前, SpringMan, unique:4...
    - detailed:もっと詳しい部位とか
    - lookingPosOnGlobal:注視主体頭部から注視対象ベクトル方向をZ軸，上向きをY軸として中心を注視対象中心とした座標系のXY平面上と注視ベクトルの交点の世界座標
    - lookingPosOnHeadCenterCoordination:注視主体頭部から注視対象ベクトル方向をZ軸，上向きをY軸として中心を注視対象中心とした座標系のXY平面上と注視ベクトルの交点，単純に原点からの距離でどれくらい注視が離れているかがわかる
    - targetDistance:↑の交点までの注視主体からの距離

- ユニークIDがついている人が指差している情報(指していないとnone)+lookdetailedatはより詳細な部位
```
  UniquePeoplePointObject={\"uniquepeoplepointobject\":[{"hid":4, "pointat":"SpringMan", "stable":true}, {"hid":2, "pointat":"unique:4", "stable":false}, {"hid":3, "pointat":"none"}]}
```

#### ロボットユーザの視線状態
- EyeContactState=MUTUALGAZE/ROBOTLOOKSHUMAN/HUMANLOOKSROBOT/NONE

#### ユーザの動きに基づく危険状態検出
- mainユーザが顔や手を近づけてきた状態
	DangerousState=HUMANHEAD2ROBOTHEAD/HUMANRIGHTHAND2ROBOTHEAD/HUMANLEFTHAND2ROBOTHEAD/HUMANRIGHTHAND2ROBOTRIGHTHAND/HUMANRIGHTHAND2ROBOTLEFTHAND/HUMANLEFTHAND2ROBOTRIGHTHAND/HUMANLEFTHAND2ROBOTLEFTHAND/NONE

- ユニークIDがついている人のロボットに対する危険状態
```
  UniquePeopleDangerousState={\"uniquepeopledangerousstate\":[{"hid":4, "dangerousstate":"HUMANHEAD2ROBOTHEAD"}, {"hid":2, "dangerousstate":"HUMANRIGHTHAND2ROBOTLEFTHAND:4"}, {"hid":3, "dangerousstate":"NONE"}]}
```

- SpeechState:RobotProsody/ListeningProsody=SpeechStart/SpeechEnd/SpeechPause

#### 感情状態が変化したとき
- MentalState=arousal=float
- MentalState=valence=float
- MentalState=smoothed_arousal=float
- MentalState=smoothed_valence=float

#### Attractivenessが変化したとき
- startattractive={\"attractiveness\":" float ", \"partName\":\""HeadController or BodyController or StanceController"\"}
- finishattractive={\"attractiveness\":" float ", \"partName\":\""HeadController or BodyController or StanceController"\"}

#### Humanや仮想オブジェクトやその他ロボットのオブジェクト結果（デフォルトでは送られてこない）
sendObjectData=true\nを送りつけると送られてくる

```
Objects=[{"rootName":"base","exportedAtMs":1770367964846,"unityVersion":"2021.3.45f2","root":{"name":"base","relativePath":"base","worldPosition":{"x":0.0,"y":1.600000023841858,"z":3.0},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":-1.0},"localScale":{"x":-0.10000000149011612,"y":0.10000000149011612,"z":0.10000000149011612},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.0,"g":0.5,"b":0.5,"a":0.5}],"meshName":"Cube"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"base","lookTarget":false,"pointingTarget":false}}},{"rootName":"option_1_real","exportedAtMs":1770367964846,"unityVersion":"2021.3.45f2","root":{"name":"option_1_real","relativePath":"option_1_real","worldPosition":{"x":1.5,"y":1.600000023841858,"z":2.5},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":-1.0},"localScale":{"x":-0.30000001192092898,"y":0.30000001192092898,"z":0.30000001192092898},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.0,"g":1.0,"b":0.0,"a":0.800000011920929}],"meshName":"Cube"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"option_1_real","lookTarget":false,"pointingTarget":false}}},{"rootName":"option_1_screen","exportedAtMs":1770367964846,"unityVersion":"2021.3.45f2","root":{"name":"option_1_screen","relativePath":"option_1_screen","worldPosition":{"x":-0.5,"y":1.600000023841858,"z":-0.5},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":-1.0},"localScale":{"x":-0.30000001192092898,"y":0.30000001192092898,"z":0.30000001192092898},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.0,"g":0.5,"b":1.0,"a":0.800000011920929}],"meshName":"Cube"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"option_1_screen","lookTarget":false,"pointingTarget":false}}},{"rootName":"option_2_real","exportedAtMs":1770367964846,"unityVersion":"2021.3.45f2","root":{"name":"option_2_real","relativePath":"option_2_real","worldPosition":{"x":2.5,"y":1.600000023841858,"z":1.5},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":-1.0},"localScale":{"x":-0.30000001192092898,"y":0.30000001192092898,"z":0.30000001192092898},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.0,"g":1.0,"b":0.0,"a":0.800000011920929}],"meshName":"Cube"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"option_2_real","lookTarget":false,"pointingTarget":false}}},{"rootName":"option_2_screen","exportedAtMs":1770367964846,"unityVersion":"2021.3.45f2","root":{"name":"option_2_screen","relativePath":"option_2_screen","worldPosition":{"x":0.5,"y":1.600000023841858,"z":-0.5},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":-1.0},"localScale":{"x":-0.30000001192092898,"y":0.30000001192092898,"z":0.30000001192092898},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.0,"g":0.5,"b":1.0,"a":0.800000011920929}],"meshName":"Cube"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"option_2_screen","lookTarget":false,"pointingTarget":false}}},{"rootName":"screen","exportedAtMs":1770367964846,"unityVersion":"2021.3.45f2","root":{"name":"screen","relativePath":"screen","worldPosition":{"x":1.5,"y":1.5,"z":0.5},"worldRotation":{"x":0.0,"y":0.3826834261417389,"z":0.0,"w":-0.9238795042037964},"localScale":{"x":-0.800000011920929,"y":1.2000000476837159,"z":0.20000000298023225},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.0,"g":0.0,"b":1.0,"a":0.800000011920929}],"meshName":"Cube"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"screen","lookTarget":false,"pointingTarget":false}}}]
```


```
Humans=[{"rootName":"unique:9","exportedAtMs":1770367964847,"unityVersion":"2021.3.45f2","root":{"name":"unique:9","relativePath":"","worldPosition":{"x":0.0,"y":0.0,"z":0.0},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":1.0},"localScale":{"x":1.0,"y":1.0,"z":1.0},"mesh":{"hasMeshRenderer":false,"materialColors":[],"meshName":""},"children":[{"name":"HumanPelvis","relativePath":"unique:9/HumanPelvis","worldPosition":{"x":0.6173795461654663,"y":0.956928014755249,"z":1.819597601890564},"worldRotation":{"x":0.12950898706912995,"y":0.5654749870300293,"z":0.1476432979106903,"w":-0.8010411858558655},"localScale":{"x":0.10000000149011612,"y":0.02500000037252903,"z":0.10000000149011612},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanSpine","relativePath":"unique:9/HumanSpine","worldPosition":{"x":0.6463830471038818,"y":1.1816681623458863,"z":1.830843448638916},"worldRotation":{"x":0.07195314764976502,"y":-0.5482174158096314,"z":-0.010580882430076599,"w":0.8331677317619324},"localScale":{"x":0.2632053792476654,"y":0.2257358431816101,"z":0.19740402698516847},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanHead","relativePath":"unique:9/HumanHead","worldPosition":{"x":0.637225329875946,"y":1.5671532154083253,"z":1.8831441402435303},"worldRotation":{"x":0.32135364413261416,"y":-0.5285080075263977,"z":0.1495550274848938,"w":0.7713912129402161},"localScale":{"x":0.16085748374462129,"y":0.10972210764884949,"z":0.16085748374462129},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftHand","relativePath":"unique:9/HumanLeftHand","worldPosition":{"x":0.4206523597240448,"y":0.942579984664917,"z":1.687368631362915},"worldRotation":{"x":-0.7757131457328796,"y":-0.4291481077671051,"z":0.09421958029270172,"w":0.45301613211631777},"localScale":{"x":0.02500000037252903,"y":0.02500000037252903,"z":0.05000000074505806},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightHand","relativePath":"unique:9/HumanRightHand","worldPosition":{"x":0.4269302487373352,"y":0.91153883934021,"z":2.05139422416687},"worldRotation":{"x":-0.6065438389778137,"y":-0.7797186374664307,"z":0.06970714032649994,"w":0.13886818289756776},"localScale":{"x":0.02500000037252903,"y":0.02500000037252903,"z":0.05000000074505806},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftThumb","relativePath":"unique:9/HumanLeftThumb","worldPosition":{"x":0.40316951274871828,"y":0.9742947816848755,"z":1.6720572710037232},"worldRotation":{"x":-0.7568997740745544,"y":-0.2316458523273468,"z":-0.18119044601917268,"w":0.5836206078529358},"localScale":{"x":0.009999998845160008,"y":0.007999999448657036,"z":0.029999995604157449},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightThumb","relativePath":"unique:9/HumanRightThumb","worldPosition":{"x":0.4190630614757538,"y":0.897869348526001,"z":2.0193519592285158},"worldRotation":{"x":-0.5207754373550415,"y":-0.7526034712791443,"z":0.32989558577537539,"w":-0.23140840232372285},"localScale":{"x":0.009999998845160008,"y":0.00800000037997961,"z":0.029999995604157449},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftFingers","relativePath":"unique:9/HumanLeftFingers","worldPosition":{"x":0.40536263585090639,"y":0.9621193408966065,"z":1.7219605445861817},"worldRotation":{"x":-0.8321771621704102,"y":-0.28568199276924136,"z":0.1719818264245987,"w":0.44304531812667849},"localScale":{"x":0.009999998845160008,"y":0.02499999850988388,"z":0.03999999538064003},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightFingers","relativePath":"unique:9/HumanRightFingers","worldPosition":{"x":0.3945118486881256,"y":0.8879434466362,"z":2.062533140182495},"worldRotation":{"x":0.4873526096343994,"y":0.863508939743042,"z":-0.07770609110593796,"w":-0.10393086075782776},"localScale":{"x":0.009999998845160008,"y":0.02499999850988388,"z":0.03999999538064003},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftThigh","relativePath":"unique:9/HumanLeftThigh","worldPosition":{"x":0.3900602459907532,"y":0.9093297123908997,"z":1.7432928085327149},"worldRotation":{"x":0.434444397687912,"y":0.5398255586624146,"z":0.4182347059249878,"w":-0.5873041152954102},"localScale":{"x":0.08211156725883484,"y":0.2052789181470871,"z":0.08211156725883484},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightThigh","relativePath":"unique:9/HumanRightThigh","worldPosition":{"x":0.4785136580467224,"y":0.8892973065376282,"z":2.005007266998291},"worldRotation":{"x":0.5009918212890625,"y":0.3378450274467468,"z":0.32071301341056826,"w":-0.7293909788131714},"localScale":{"x":0.08202309906482697,"y":0.205057755112648,"z":0.08202309906482697},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}}],"metaData":{"isHuman":true,"id":9,"area_id":-1,"has_unique":true,"objectId":"","lookTarget":false,"pointingTarget":false}}},{"rootName":"unique:10","exportedAtMs":1770367964847,"unityVersion":"2021.3.45f2","root":{"name":"unique:10","relativePath":"","worldPosition":{"x":0.0,"y":0.0,"z":0.0},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":1.0},"localScale":{"x":1.0,"y":1.0,"z":1.0},"mesh":{"hasMeshRenderer":false,"materialColors":[],"meshName":""},"children":[{"name":"HumanPelvis","relativePath":"unique:10/HumanPelvis","worldPosition":{"x":-1.3902345895767213,"y":0.7571322321891785,"z":2.1214516162872316},"worldRotation":{"x":-0.023099001497030259,"y":0.8879358172416687,"z":0.1428161859512329,"w":0.43662330508232119},"localScale":{"x":0.10000000149011612,"y":0.02500000037252903,"z":0.10000000149011612},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanSpine","relativePath":"unique:10/HumanSpine","worldPosition":{"x":-1.425869107246399,"y":0.9608045816421509,"z":2.169100522994995},"worldRotation":{"x":-0.022112248465418817,"y":0.8706097602844238,"z":0.13839635252952577,"w":0.47158893942832949},"localScale":{"x":0.22191736102104188,"y":0.21150222420692445,"z":0.1664380133152008},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanHead","relativePath":"unique:10/HumanHead","worldPosition":{"x":-1.3630458116531373,"y":1.304392695426941,"z":2.141928195953369},"worldRotation":{"x":0.1272096037864685,"y":0.9097721576690674,"z":-0.1542058289051056,"w":0.3638034164905548},"localScale":{"x":0.18050235509872437,"y":0.11522547155618668,"z":0.18050235509872437},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftHand","relativePath":"unique:10/HumanLeftHand","worldPosition":{"x":-1.157589316368103,"y":0.9802018404006958,"z":2.18255615234375},"worldRotation":{"x":-0.3531472980976105,"y":0.5617583394050598,"z":0.708440899848938,"w":0.24047040939331056},"localScale":{"x":0.02500000037252903,"y":0.02500000037252903,"z":0.05000000074505806},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightHand","relativePath":"unique:10/HumanRightHand","worldPosition":{"x":-1.4011975526809693,"y":0.7592281699180603,"z":1.9834727048873902},"worldRotation":{"x":0.11589087545871735,"y":0.06601312011480332,"z":0.3896876275539398,"w":0.9112382531166077},"localScale":{"x":0.02500000037252903,"y":0.02500000037252903,"z":0.05000000074505806},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftThumb","relativePath":"unique:10/HumanLeftThumb","worldPosition":{"x":-1.1682054996490479,"y":1.0143378973007203,"z":2.1820855140686037},"worldRotation":{"x":-0.5992454290390015,"y":0.6120216250419617,"z":0.5160202383995056,"w":0.007587525527924299},"localScale":{"x":0.009999998845160008,"y":0.007999999448657036,"z":0.029999995604157449},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightThumb","relativePath":"unique:10/HumanRightThumb","worldPosition":{"x":-1.4093217849731446,"y":0.7450121641159058,"z":2.031510829925537},"worldRotation":{"x":0.233291894197464,"y":-0.24078936874866486,"z":0.3238670825958252,"w":0.884706437587738},"localScale":{"x":0.009999998845160008,"y":0.00800000037997961,"z":0.029999995604157449},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftFingers","relativePath":"unique:10/HumanLeftFingers","worldPosition":{"x":-1.1293154954910279,"y":0.9895905256271362,"z":2.158191680908203},"worldRotation":{"x":-0.3572608530521393,"y":0.5629045963287354,"z":0.7055047750473023,"w":0.24034614861011506},"localScale":{"x":0.009999998845160008,"y":0.02499999850988388,"z":0.03999999538064003},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightFingers","relativePath":"unique:10/HumanRightFingers","worldPosition":{"x":-1.3893595933914185,"y":0.7270277738571167,"z":1.9864846467971802},"worldRotation":{"x":0.10828497260808945,"y":0.07672059535980225,"z":0.384173721075058,"w":0.9136732816696167},"localScale":{"x":0.009999998845160008,"y":0.02499999850988388,"z":0.03999999538064003},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanLeftThigh","relativePath":"unique:10/HumanLeftThigh","worldPosition":{"x":-1.1724835634231568,"y":0.686937153339386,"z":2.1635968685150148},"worldRotation":{"x":-0.36356115341186526,"y":0.6217081546783447,"z":0.43637415766716006,"w":0.5393328666687012},"localScale":{"x":0.07030005753040314,"y":0.17575013637542725,"z":0.07030005753040314},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"HumanRightThigh","relativePath":"unique:10/HumanRightThigh","worldPosition":{"x":-1.3132150173187256,"y":0.7147641181945801,"z":1.9447697401046754},"worldRotation":{"x":-0.23256178200244904,"y":0.7080163359642029,"z":0.5527392029762268,"w":0.3729707896709442},"localScale":{"x":0.07030000537633896,"y":0.1757500171661377,"z":0.07030000537633896},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":0.7843137383460999,"g":1.0,"b":0.6274510025978088,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}}],"metaData":{"isHuman":true,"id":10,"area_id":-1,"has_unique":true,"objectId":"","lookTarget":false,"pointingTarget":false}}}]
```

```
- Robots=[{"rootName":"MH.01","exportedAtMs":1770367964707,"unityVersion":"2021.3.45f2","root":{"name":"MH.01","relativePath":"","worldPosition":{"x":0.0,"y":0.0,"z":0.0},"worldRotation":{"x":0.0,"y":0.0,"z":0.0,"w":1.0},"localScale":{"x":1.0,"y":1.0,"z":1.0},"mesh":{"hasMeshRenderer":false,"materialColors":[],"meshName":""},"children":[{"name":"SpineYaw","relativePath":"MH.01/SpineYaw","worldPosition":{"x":1.384889006614685,"y":0.9476708173751831,"z":-0.8016427159309387},"worldRotation":{"x":4.3785101411231155e-7,"y":0.8653957843780518,"z":-0.0000015316439885282307,"w":0.5010890960693359},"localScale":{"x":0.20000000298023225,"y":0.019999999552965165,"z":0.20000000298023225},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":1.0,"g":1.0,"b":1.0,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"Spine","relativePath":"MH.01/Spine","worldPosition":{"x":1.385923981666565,"y":1.1314680576324463,"z":-0.8013718724250794},"worldRotation":{"x":0.002670066896826029,"y":0.8653932213783264,"z":-0.0007362542091868818,"w":0.5010859966278076},"localScale":{"x":0.25,"y":0.19314999878406526,"z":0.20000000298023225},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":1.0,"g":1.0,"b":1.0,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"Head","relativePath":"MH.01/Head","worldPosition":{"x":1.4347820281982422,"y":1.595654010772705,"z":-0.8289552927017212},"worldRotation":{"x":-0.0009130039252340794,"y":0.8648955225944519,"z":-0.014454989694058895,"w":0.5017433166503906},"localScale":{"x":0.1599999964237213,"y":0.125,"z":0.18000000715255738},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":1.0,"g":1.0,"b":1.0,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"LeftHand","relativePath":"MH.01/LeftHand","worldPosition":{"x":1.9406789541244507,"y":0.7555102705955505,"z":-0.8727359175682068},"worldRotation":{"x":-0.17265650629997254,"y":0.7034494280815125,"z":0.46430060267448428,"w":0.5096806287765503},"localScale":{"x":0.05000000074505806,"y":0.05000000074505806,"z":0.02500000037252903},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":1.0,"g":1.0,"b":1.0,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"RightHand","relativePath":"MH.01/RightHand","worldPosition":{"x":1.7254530191421509,"y":0.7557064890861511,"z":-1.2465219497680665},"worldRotation":{"x":-0.31363651156425478,"y":0.7934008836746216,"z":0.3821476995944977,"w":0.3551205098628998},"localScale":{"x":0.05000000074505806,"y":0.05000000074505806,"z":0.02500000037252903},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":1.0,"g":1.0,"b":1.0,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"LeftEyeBody","relativePath":"MH.01/LeftEyeBody","worldPosition":{"x":1.5392999649047852,"y":1.606850028038025,"z":-0.8487619757652283},"worldRotation":{"x":0.0016693089855834842,"y":0.8780540823936462,"z":-0.018507549539208413,"w":0.47820109128952029},"localScale":{"x":0.009999996982514859,"y":0.009999999776482582,"z":0.009999996982514859},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":1.0,"g":1.0,"b":1.0,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}},{"name":"RightEyeBody","relativePath":"MH.01/RightEyeBody","worldPosition":{"x":1.5045570135116578,"y":1.6057050228118897,"z":-0.9095206260681152},"worldRotation":{"x":0.001143916044384241,"y":0.8529924750328064,"z":-0.018330689519643785,"w":0.5216004252433777},"localScale":{"x":0.009999996982514859,"y":0.009999999776482582,"z":0.009999996982514859},"mesh":{"hasMeshRenderer":true,"materialColors":[{"r":1.0,"g":1.0,"b":1.0,"a":0.30000001192092898}],"meshName":"Capsule"},"children":[],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"","lookTarget":false,"pointingTarget":false}}],"metaData":{"isHuman":false,"id":0,"area_id":0,"has_unique":false,"objectId":"MH.01","lookTarget":true,"pointingTarget":true}}}]
```

#### その他
- 視線を外したタイミングもストリーミング
  - GazeAvert={"pitch":float, "yaw":float}

### 警告
- Warning

Warning=メッセージ\n
- Error

Error=メッセージ\n

# How to make gesture
- オブジェクトからの相対でジェスチャーを作る場合
  - 向きは標準状態での向きをしていする
  - 位置は2種類ありオブジェクトのローカル座標系での位置とオブジェクトからみた顔の向き（Look）をZ方向とした座標系
- その他注意点
  - GreetingではRollを０にするとしゃきっと動作になる

# UnityEditor
MainCamera/LocalEnvSetterで環境名を入れることでUnityEditorで起動する場合でも環境を設定できる

# その他
## カメラ平面の3次元プロジェクション
- SpringMan/EyeCameraController/CameraImage
向かって左がX，上がY
