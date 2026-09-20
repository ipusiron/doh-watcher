# DoH Watcher開発ガイド

このリポジトリーはGoogle Colabで動かすノートブック1本と説明・テスト・画像から構成されます。公開先はGitHub／Colabで、GitHub Pagesは使いません。

## 構成とセルID

| セルID | 役割 |
|---|---|
| 175bf3fb | 概要（既存） |
| 5c8468fb | 設定：domains、query_count=5、timeout=5、warmup=1、mode='both'（既存） |
| 403835be | requests・pandas・matplotlibとsocketの読み込み（既存） |
| d015-method | 測定条件と限界の説明 |
| d015-wire | core：DNS wireformat、base64url、圧縮名の解析 |
| d015-stats | core：統計、シナリオ生成、transportを引数で受ける計測ループ |
| 454ee782 | Google／CloudflareとOSリゾルバーへの通信（既存） |
| 3091daf0 | 測定とシナリオ別の集計表（既存） |
| 7b3f507d | matplotlibによる中央値のグラフ（既存） |
| 506a753b | 学びのポイント、DNSSEC、送信先の説明（既存） |
| d015-dnssec | 両プロバイダーでDOあり／なしのADを観察 |

既存7セルのIDを変更せず、追加したセルには重複しないIDを付けます。すべてのコードセルはoutputs=[]、execution_count=nullの状態でコミットします。

## 測定の設計

- repeatは同じ名前を繰り返す。uniqueは毎回16桁のランダムな16進数を付ける。
- uniqueでも委任情報や否定応答などのキャッシュは残り、完全な冷キャッシュを保証しない。
- DoHは毎回新しいSessionを作る条件と、プロバイダーごとのSessionを再利用する条件を分ける。
- 各条件のウォームアップは1回で、集計から除く。条件順はランダム化する。
- perf_counterで計測し、平均・中央値・p95・最小・最大・標本標準偏差・n・失敗件数を出す。
- NXDOMAINとNODATAは有効な応答として計測する。OS APIは両者とADを判別できない。
- 失敗は時間の統計から除き、一覧とグラフの失敗件数に表示する。ウォームアップの失敗も一覧に残す。
- JSON APIは各社独自形式、wireformatはRFC 8484である。modeはjson／wire／bothを受ける。
- HTTPSはtimeoutを必ず指定し、リダイレクト・再試行・環境の認証情報を使わない。401は直ちに停止する。

## テスト

```console
python -m unittest discover -s tests -v
```

tests/nbloader.pyは標準ライブラリーでJSONを読み、coreタグ付きセルをcompile・execします。coreはネットワーク通信も外部パッケージのimportも行いません。
CIはPython 3.11／3.12で同じコマンドを実行し、pip installは行いません。
wireformatの既知解答と統計の期待値を変えて実装に合わせることは禁止します。実ネットワークの時間やADは変動するため、固定値の単体テストにはしません。

## ドキュメントと画像

READMEは設定、測定条件、依存3パッケージ、セルの実態と一致させます。先頭YAMLのid・slug・repo_url・demo_url・hubとキー構造を保ちます。
assets/の3枚は実測グラフです。既存のimages/は変更しません。グラフは1200×720、300KB以下、英語のラベルで保存します。
再生成スクリプトは対象リポジトリー外のbusiness/research/try100_audit/impl/shots/day015_shots.pyにあります。実測データを捏造せず、測定条件と失敗件数を併記します。

## やらないこと

- 依存パッケージやプロバイダーを追加しない。通信先はGoogle・CloudflareとOSリゾルバーに限る。
- seabornパッケージをimportしない。matplotlib同梱のスタイル名seaborn-v0_8-whitegridだけは使用する。
- ノートブックからリポジトリー内の外部ファイルをimportしない。pip installやgit cloneを入れない。
- 認証情報、閲覧履歴、個人情報を収集しない。例外の生文字列を表示しない。
- 既存画像、既存セルIDを変更しない。実行結果をノートブックへ保存しない。
- 測定した速度やプロバイダー順位を一般化しない。管理していないドメインで回数を増やさない。
