# MiracleHuman ドキュメント

MiracleHuman は Unity の `ArticulationBody` でヒューマノイドのジョイントを定義し、視線・頭部・体幹・腕・手指・表情・内部状態などの複数モジュールを組み合わせて全身制御を行うアプリケーションです。

README が長大になりやすいため、詳細は次の 3 ファイルに分割しています。

## 分割ドキュメント

1. [システム概要と使い方](./MiracleHuman_System_Usage.md)
   - 起動方法
   - TCP 通信方式
   - ControllerASync / ControllerSync / Streaming の概要
   - ターゲット指定、仮想オブジェクト、カメラ、モーター送信制御などの運用コマンド

2. [ArticulationBody 制御モジュールと親子関係](./MiracleHuman_ArticulationBody_Modules.md)
   - `ArticulationBody` ベースのジョイント制御の考え方
   - Eye / Head / Body / Hand / Trunk / Stance / FACS などの制御モジュール
   - モジュール間の親子関係・優先度・連動関係
   - Streaming で取得できるジョイント状態

3. [Motion・FACS・Action の機能別説明と定義方法](./MiracleHuman_Motion_FACS_Action.md)
   - 定義済み Motion / Sequence Motion の再生
   - 未定義 Motion / HandMotion / AngleMotion の JSON 定義
   - FACS・ManualFACS・Blink の定義
   - Action による Motion / Facial / Attractiveness / Controller の合成

## 注意

- コマンド文字列では、`=` の前後にスペースを入れないでください。
- TCP コマンドのフッターは基本的に改行コード `\n` です。
- 座標系は、ロボットの正面が `z` 軸、右が `x` 軸、上が `y` 軸の左手座標系です。原点はロボットの腰下付近、単位はメートルです。
