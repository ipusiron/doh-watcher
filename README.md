<!--
---
id: day015
slug: doh-watcher

title: "DoH Watcher"

subtitle_ja: "DNS over HTTPS の効果を実測して比べる教育ツール"
subtitle_en: "Measure and compare the effect of DNS over HTTPS"

description_ja: "通常のDNSとDoH（Google／Cloudflare）の応答時間を、キャッシュの有無と接続の再利用の有無で分けて実測し、比較するGoogle Colabノートブックです。RFC 8484のwireformatとJSON APIの違い、DNSSECのADフラグも観察できます。"
description_en: "A Google Colab notebook that measures and compares DNS response times between standard DNS and DoH (Google / Cloudflare), separating cached and uncached lookups and reused and new connections. It also shows the difference between RFC 8484 wireformat and JSON APIs, and the DNSSEC AD flag."

category_ja:
  - ネットワーク
category_en:
  - Network

difficulty: 2

tags:
  - dns
  - doh
  - privacy
  - network
  - colab

repo_url: "https://github.com/ipusiron/doh-watcher"
demo_url: "https://colab.research.google.com/github/ipusiron/doh-watcher/blob/main/doh_watcher.ipynb"

hub: true
---
-->

# DoH Watcher - DNS over HTTPS効果観察ツール

[English](README.en.md) · 日本語

![GitHub stars](https://img.shields.io/github/stars/ipusiron/doh-watcher?style=social)
![GitHub forks](https://img.shields.io/github/forks/ipusiron/doh-watcher?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/ipusiron/doh-watcher)
![GitHub license](https://img.shields.io/github/license/ipusiron/doh-watcher)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ipusiron/doh-watcher/blob/main/doh_watcher.ipynb)

**Day015 - 生成AIで作るセキュリティツール100**

**DoH Watcher**は、DNS over HTTPS（DoH）の実際の効果を体験的に学べる教育向けツールです。
Google Colab上で動作し、同じ名前の反復とユニークな名前、新規接続と接続再利用を分けて「通常のDNS」と「DoH」を比較できます。
RFC 8484のwireformatとJSON APIによる問い合わせ、DNSSECのADフラグも観察できます。

---

## 🌐 デモページ

👉 [Colabで開く](https://colab.research.google.com/github/ipusiron/doh-watcher/blob/main/doh_watcher.ipynb)

---

## 📸 スクリーンショット

グラフは2026-09-20のローカル環境で実測した値です。各条件の成功件数は5、失敗件数は0で、ウォームアップ1回を除いています。数値や順位は環境によって変わります。

![Colabで実行しているところ](images/screenshot1.png)
> *Colabで実行する操作の参考画面です。改修前のノートブックを表示しています。*

![repeatの実測グラフ](assets/screenshot.png)
> *repeatでは、通常DNSがキャッシュに命中したと考えられる短い応答時間になりました。DoHはwireformat・接続再利用です。*

![uniqueの実測グラフ](assets/screenshot2.png)
> *uniqueでは同じ名前のキャッシュを避け、通常DNSと接続再利用したDoHの差が縮まりました。否定応答も集計に含みます。*

![新規接続と接続再利用の実測グラフ](assets/screenshot3.png)
> *repeat・wireformatでの新規接続と接続再利用の比較です。接続確立コストの違いを観察できます。*

測定条件で結論が変わります。通常DNSが速く見える理由の1つはOSリゾルバーのキャッシュです。同じ名前のキャッシュを避けるとDoHとの差は縮むことがあり、環境によってはDoHのほうが速くなります。
DoHではTLS/TCPの接続確立コストが遅延の大きな要因になり、接続を再利用すると改善できます。ただし、その差にはサーバーの負荷や通信経路の変動も含まれます。
**プロバイダーの優劣は測定した場所・時刻・経路で入れ替わります。1回の測定で恒常的な順位を決めないでください。**

---

## ✨ 機能

| 機能                         | 説明                                                                 |
|------------------------------|----------------------------------------------------------------------|
| DoHによるDNS応答取得 | Google／CloudflareのJSON APIとRFC 8484のwireformat |
| 応答時間の測定 | 平均・中央値・p95・最小・最大・標本標準偏差・成功件数n・失敗件数 |
| グラフによる可視化 | 中央値を棒の高さとし、失敗件数とウォームアップの除外を明示 |
| 通常DNSとの比較 | repeat／uniqueを分け、DoHの新規接続／接続再利用も区別 |
| DNSSECの観察 | DOビットの有無によるADフラグの違い |
| Markdown解説 | ネットワークとDNSの基礎、測定の限界、送信先の説明 |

---

## 📖 使い方

1. 「Colabで開く」を選ぶ。またはGitHubから`doh_watcher.ipynb`をダウンロードしてColabに開く。
2. 設定セルの`domains`、`query_count = 5`、`timeout = 5`、`warmup = 1`を確認する。他者のドメインで回数を増やさない。
3. `mode`を`'json'`／`'wire'`／`'both'`から選び、上から順にセルを実行する。[Shift]＋[Enter]キー、または「ランタイム」→「すべてのセルを実行」を使う。
4. シナリオごとの表と中央値の棒グラフを読む。最後のセルでDNSSECのADフラグを比較する。

失敗は例外種別と安全な説明を表示し、時間の統計から除きます。ウォームアップ中の失敗も一覧に残します。HTTP 401では再試行せず停止します。認証情報を入力する機能はありません。

---

## 🔬 技術的な説明

### 測定条件と統計

| 条件 | 内容と限界 |
|---|---|
| repeat | 同じ名前を反復。OSや再帰リゾルバーのDNSキャッシュの影響あり |
| unique | 毎回16桁のランダムな16進数を付加。NXDOMAIN／NODATAも有効な応答として計測 |
| new connection | 毎回新しいrequests.Sessionを作成し、終了時に破棄 |
| reused connection | プロバイダーごとに1つのSessionを再利用 |

requests自体にはHTTP応答キャッシュがありませんが、DoHプロバイダーにもDNSキャッシュがあります。uniqueでも委任情報、否定応答やDNSSECの否定証明のキャッシュまで消せるわけではなく、完全な冷キャッシュを保証しません。ワイルドカードの設定がある名前では肯定応答になる場合もあります。

各条件にウォームアップを設け、条件の実行順をランダム化しています。`time.perf_counter()`で応答の読み取り・解析までを測り、新規接続ではSessionの作成・終了も含みます。OSのAPIではNXDOMAINとNODATAを区別できないため、まとめて否定応答として扱います。

p95は昇順の値の位置`(n - 1) × 0.95`を線形補間して求めます。標準偏差は標本標準偏差です。成功が1件なら標準偏差は0、0件なら時間の統計はNoneとし、棒には「no data」を表示します。5回という少数の測定では、p95や平均が外れ値の影響を強く受けることにも注意してください。

### JSON APIとwireformat

JSON APIはRFC 8484ではなく、GoogleとCloudflareの独自APIです。wireformatはDNSのバイナリメッセージを`application/dns-message`として受け取り、GETの`dns`パラメーターにはパディングなしbase64urlを指定します。

| プロバイダー | JSON API | wireformat |
|---|---|---|
| Google | `https://dns.google/resolve` | `https://dns.google/dns-query` |
| Cloudflare | `https://cloudflare-dns.com/dns-query` | `https://cloudflare-dns.com/dns-query` |

JSONは`accept: application/dns-json`、wireformatは`accept: application/dns-message`を指定します。名前圧縮とA・AAAA・CNAMEの解析に対応し、DOありではUDPペイロードサイズ1232のOPT RRを付けます。

Quad9（dns.quad9.net）はHTTP/2を必須とするため、requests（HTTP/1.1）からは505が返り、このノートブックからは利用できません。

### DoHとDNSSEC

DoHは端末とプロバイダーの間の経路を暗号化し、DNSSECは署名によってDNSデータの真正性を検証します。ノートブックは署名を独自に検証せず、リゾルバーから返るADを表示します。
2026-09-20の実測では、両プロバイダーともexample.comはDOありでAD=True、DOなしでAD=Falseでした。google.comはDOの有無によらずAD=Falseでした。署名状態やリゾルバーの方針は変わるため、固定の正解として扱わないでください。

### ✅ 通常のDNS（暗号化なし）

- 従来のDNSはUDPまたはTCPのポート53を使い、問い合わせと応答を平文で通信する。
- 経路上で通信を観測できる第三者にドメイン名が見える。OSが暗号化DNSを使う構成もあるため、この比較の「Standard DNS」はOS設定に依存する。

---

### ✅ DoH（DNS over HTTPS）のしくみ

DoHでは、**DNSクエリーそのものをHTTPS通信の中に埋め込み、Web通信と同じ経路で暗号化して送信**します。

#### 🔄 処理の流れ

1. クライアント（例：ブラウザー）がドメイン名の解決を要求する。
2. HTTPSのリクエストとしてDoHサーバーに送信する。このノートブックではGETを使う。
3. クエリーをTLSで暗号化し、経路上の第三者から内容を保護する。
4. DoHサーバーがDNSの応答をHTTPSで返す。

---

### 🛡️ 守られるもの

| 守られる情報           | 通常DNSでは？     | DoHでは？                  |
|------------------------|------------------|----------------------------|
| クエリー内容（ドメイン名） | 見える            | 見えない（TLSで暗号化）     |
| 送信先DNSサーバー       | 見える            | HTTPSの接続先IPアドレスなどは見える |
| 改ざん耐性              | なし             | TLSにより検知・排除可能     |

---

### 📦 技術的には何を使っているの？

- **TLS（Transport Layer Security）**：HTTPSと同じ暗号化層を使用
- **HTTPSのリクエスト形式**：DNSクエリーをURLパラメーターとして送信
- **DoHサーバーのエンドポイント例**：`https://dns.google/dns-query`など

---

### 🧠 教育的に観察する項目

- **クエリー内容の保護**：経路上の第三者から問い合わせ内容を隠す。ただし、Web接続先など別の通信から推測される可能性は残る。

- **HTTPS接続の再利用**：TLS/TCP接続を毎回確立する場合との時間差を調べる。企業・学校ではネットワーク管理の方針にも注意する。

---

DoHは、HTTPSという既存のインフラを活かしてDNSの脆弱性を解決しようとする、現代インターネット設計の好例です。

## 📚 教育目的での使い方

### 🧠 このツールで学べること

| テーマ             | 内容                                                                 |
|--------------------|----------------------------------------------------------------------|
| DNSの仕組み         | IPアドレスを得るための名前解決プロセスを学びます。                    |
| 暗号化通信          | HTTPSによりDNSクエリー内容が秘匿される利点を実感できます。               |
| プライバシーの保護  | DoHがユーザーの通信を守る一方で、監視が難しくなる点も理解できます。     |
| 遅延とトレードオフ  | DoH導入による応答遅延とプライバシー向上のバランスを考察できます。       |

---

### 🎓 ステップアップの方向性

| レベル | 学習課題                                                                 |
|--------|--------------------------------------------------------------------------|
| 初級   | DNSとは何か？　名前解決とは？　HTTPとHTTPSの違いとは？                      |
| 中級   | DoHのAPIの仕様や、TLSハンドシェイクの流れを理解する                      |
| 上級   | DNSSECやDoT（DNS over TLS）との違いを検証・トラフィック分析や可視化へ拡張 |

#### 🔰 初級：DNSとHTTPSの基礎理解から始めよう（〜高校情報IIレベル）
まずはDNSの役割と仕組み（名前解決とは何か）を理解しましょう。
ドメイン名がどのようにIPアドレスへ変換されるか、dig や nslookup を使って確認すると実感が湧きます。

次にHTTPとHTTPSの違いを学び、「通信が暗号化されるとはどういうことか」「なぜそれが重要なのか」を体験的に理解することが目標です。
DoH Watcherの実行と結果観察を通じて、測定条件による差と、OS側のDNS設定を確認する必要性を学べます。

#### 🧭 中級：DoHとTLSの動作原理を掘り下げる（高専・大学前半向け）
DoHがどのようなAPIを使って通信しているのか、クエリーとレスポンスの形式（例：JSON構造）を実際に観察しましょう。

次に、HTTPSが使用するTLSのハンドシェイク手順（証明書交換、鍵生成など）を図解やツール（openssl, Wireshark）を用いて確認することが学習の中心です。

また、通常DNSとDoHのトラフィックの違い（ポート番号、可視性）を可視化することで、「暗号化されることで何が守られるか」を深く理解できます。

#### 🧠 上級：関連技術との比較とセキュリティ観点での分析（大学・専門職向け）
DNSのセキュリティ強化技術であるDNSSECや、DoHの兄弟的存在であるDoT（DNS over TLS）と比較し、それぞれの長所短所を整理しましょう。

次に、Wireshark等を使ったパケットキャプチャーや、疑似トラフィックを使った可視化ツールの開発など、より高度なネットワーク分析に挑戦します。
加えて、企業ネットワークにおけるDoHのメリット・リスク（例：管理者が見えなくなる問題）についても多面的に考察できると、実践的な理解が身につきます。

---

## 🔒 セキュリティとプライバシー

送信先は`dns.google`・`cloudflare-dns.com`（HTTPS）と、比較に使うOSのリゾルバーです。設定セルの検証対象ドメイン名と、uniqueで生成するランダムなサブドメインを送ります。DoHサーバー自身の名前解決もOSに依存します。
個人情報・閲覧履歴・認証情報を収集する処理はありません。ただし、入力するドメイン名に個人情報や社内名を含めないでください。

**DoHプロバイダーには「誰が何を引いたか」が見えます。**経路上の第三者からクエリーを隠せても、プロバイダーへの信頼は前提です。Oblivious DoH（[RFC 9230](https://www.rfc-editor.org/rfc/rfc9230.html)）は、問い合わせ元とクエリーの内容を分離して、この問題に対処する方式です。本ツールには実装していません。

HTTPSの証明書検証は有効のままです。自動リダイレクトと再試行を行わず、環境変数のプロキシと.netrcの認証情報を使わないSessionを作ります。例外の生文字列は表示せず、種別と安全な説明を残します。HTTP 401では停止します。

## ⚠️ 注意事項

- uniqueの問い合わせは公開の権威サーバーまで到達することがある。他者が管理するドメインに対して大量に実行しない。
- キャッシュはOS・再帰リゾルバーなど複数の場所に存在する。repeatをキャッシュあり、uniqueをキャッシュなしの目安として比較しても、完全な制御実験にはならない。
- HTTPSの`timeout`は接続と読み取りの待ち時間であり、測定全体の厳密な上限ではない。OSの名前解決時間もOS設定に依存する。
- プロキシが必須の環境では通信できない場合がある。通信制限を回避するために証明書検証を無効にしない。
- 既定の5回は教育用の少数測定である。時間やプロバイダーの順位を一般化しない。

## 📦 使用ライブラリー

- `requests`：DoHクエリーの送信
- `pandas`：集計結果と失敗一覧の表
- `matplotlib`：中央値の棒グラフ

これらはGoogle Colabにプリインストールされています。標準ライブラリーの`time`は計測、`base64`・`struct`はwireformat、`statistics`は統計に使います。追加インストールは行いません。グラフのスタイル名`seaborn-v0_8-whitegrid`はmatplotlib同梱のもので、同名の外部パッケージは不要です。

## 🔗 参考

- 🔸 **さくらのナレッジ：「DNS over HTTPSを理解する」**
　図解が豊富で、DoHの基本や通常DNSとの違いを丁寧に解説。初心者に最適。
　👉 [https://ssl.sakura.ad.jp/column/doh/](https://ssl.sakura.ad.jp/column/doh/)

- 🔸 **Cloudflare公式ブログ（日本語）**
　DoHの目的、プライバシー保護の意義、実装背景などをわかりやすく紹介。
　👉 [https://blog.cloudflare.com/ja-jp/dns-encryption-explained/](https://blog.cloudflare.com/ja-jp/dns-encryption-explained/)

- 🔸 **RFC 8484 日本語訳（DNS over HTTPS仕様）**
　DoHの公式仕様文書（RFC 8484）の日本語訳。構造・プロトコルを深く理解したい人向け。
　👉 [https://tex2e.github.io/rfc-translater/html/rfc8484.html](https://tex2e.github.io/rfc-translater/html/rfc8484.html)


---

- [RFC 8484原文](https://www.rfc-editor.org/rfc/rfc8484.html)
- [Google Public DNSのJSON API](https://developers.google.com/speed/public-dns/docs/doh/json)
- [CloudflareのJSON API](https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/make-api-requests/dns-json/)

## 📁 ディレクトリー構造

```text
doh-watcher/
├── .github/
│   └── workflows/
│       └── test.yml
├── assets/
│   ├── screenshot.png
│   ├── screenshot2.png
│   └── screenshot3.png
├── images/
│   ├── screenshot1.png
│   └── screenshot2.png
├── tests/
│   ├── nbloader.py
│   ├── test_notebook.py
│   ├── test_readme.py
│   ├── test_stats.py
│   ├── test_transport.py
│   └── test_wireformat.py
├── .gitignore
├── CLAUDE.md
├── doh_watcher.ipynb
├── LICENSE
├── README.md
└── README.en.md
```

## 🧪 テスト

Python 3.11／3.12で、標準ライブラリーだけを使って実行します。依存パッケージのインストールやネットワーク通信は必要ありません。

```console
python -m unittest discover -s tests -v
```

`tests/nbloader.py`がJSONとしてノートブックを読み、`core`タグのコードセルだけを読み込みます。RFCの既知解答、圧縮名、DOビット、統計量、ウォームアップ、失敗件数、Sessionの再利用、READMEの記載を検証します。GitHub Actionsでもpushとpull_requestのたびに同じテストを実行します。

## 💻 動作環境

実行環境はGoogle Colabです。ノートブック単体で上から順に実行でき、リポジトリー内の外部Pythonファイルには依存しません。
ローカルで測定する場合は、requests・pandas・matplotlibが利用できるPython環境が必要です。テストだけならPython 3.11以上の標準ライブラリーで実行できます。

## 📄 ライセンス

MIT License - [LICENSE](LICENSE)ファイルを参照

---

## 🛠️ このツールについて

本ツールは、「生成AIで作るセキュリティツール100」プロジェクトの一環として開発されました。 このプロジェクトでは、AIの支援を活用しながら、セキュリティに関連するさまざまなツールを100日間にわたり制作・公開していく取り組みを行っています。

プロジェクトの詳細や他のツールについては、以下のページをご覧ください。

🔗 [https://akademeia.info/?page_id=42163](https://akademeia.info/?page_id=42163)
