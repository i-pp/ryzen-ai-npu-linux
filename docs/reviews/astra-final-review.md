# 最終技術監査 — 固定 snapshot 17f5a740

## 判定

**歴史の記録としては概ね妥当。クリーン Ubuntu からの再現手順としては未完成。クリーン環境で実証済みとは判定しない。** 本文の全面書き直しは不要だが、公開準備と補助ツールには修正を返す。

| 判定対象 | 判定 | 理由 |
|---|---|---|
| 記録として妥当 | 条件付き可 | 原ログ・保存ソースで C++ API 完了とランタイムの NPU 実行報告を裏付けられる。単独 ABI 原因、Python 3.12 成功、数値正解へ拡張していない。U/A の会話証拠は収集担当経由であり、その限界は維持する。 |
| 再現手順として十分 | 不可 | 固定入力の欠落、IRON wheel の未解決、ホスト依存導入の不足が残る。現状はゲート付き追試計画として有用。 |
| クリーン環境で実証済み | 不可・未実施 | 新規取得→展開→リンク→ロード→Run→数値比較を独立ホストで完了した証拠がない。21 fixture の成功では代用できない。 |
| そのまま公開可能 | 不可 | 追跡済み文書に非公開会話リンクが残る。LICENSE は権利付与でなく未決定通知。Zenn 上の相対リンクの公開先も未確定。 |

重要度は、BLOCKER＝その到達目標を宣言できない未達条件、MAJOR＝実用・保全・公開に影響する修正、MINOR＝限定的な修正、とする。BLOCKER は歴史記事の下書き自体を禁止する意味ではない。既知の不足を正直に書いたことを虚偽と判定してはいない。

## 修正・解消を返す finding

### R01 — BLOCKER（再現手順の完了判定）: 成功構成の入力を新規取得物へ固定できない

- **箇所:** `docs/dependencies.md:21`, `docs/dependencies.md:23`, `docs/dependencies.md:24`, `docs/mlir-aie-setup.md:10`, `docs/reproduction-procedure.md:39`, `scripts/stage-cpp-sdk.py:47`。
- **根拠:** SDK 全体、C++ ORT archive、SDK Peano wheel の完全ハッシュ／取得証跡が未回収。IRON は cp314 MLIR wheel の出所と、cp314 venv に存在する cp310 LLVM-AIE wheel の導入方法が未解決。C++ helper は任意の供給ハッシュと当該入力を照合するため、新しい取得物を自身でハッシュして渡せば、その新しい物の整合性は確認できる。しかし歴史的に成功した archive と同一であることは確認できない。モデル・ヘッダー・XRT subset の pin がある点は評価するが、全体の代替にはならない。
- **影響:** 保存ホストを参照できない別の技術者は、同一構成を確定できず、IRON 分岐は手順に従うと停止する。C++ 分岐で新規入力を採用するなら、歴史構成の復元と別の検証ベースラインを区別する必要がある。
- **最小修正:** 「同一構成の復元」と「新規取得物での追試」を明示的に分ける。前者には権利上取得可能な版・URL/認証手順・完全 SHA-256・配布物内の相対 member path を固定した manifest を用意し、helper はその reviewed manifest を参照する。後者は新規 baseline ID を付け、歴史的同一性を主張しない。IRON は対応 wheel を回収するか、別の対応構成を独立検証し、同一復元とは区別する。ハッシュを捏造して埋めない。
- **検証:** 既存 SDK/venv/cache を参照できない新 checkout から入力を取得して manifest を照合する。archive の1バイト差分は拒否されること。IRON は通常の wheel compatibility 検査・native import・compile・実行へ段階的に進み、force-install で通しただけを解消扱いしない。

### R02 — MAJOR（公開）: 非公開会話リンクが tracked docs に残る

- **箇所:** `docs/conversation-evidence.md:9`（同表の28行目まで）。
- **根拠:** 全 tracked files の限定 pattern 検査で、このファイルの20行に非公開 ChatGPT 会話 URL を検出した。記事本文にないことは確認できるが、repo 全体から排除されてはいない。読者がアクセスできる公開一次資料でもない。ここではリンク識別子自体を再掲載しない。
- **影響:** repo をそのまま公開すると、会話・メッセージ識別子と私的な参照関係が公開され、追跡可能な出典としても機能しない。リンクが第三者に会話閲覧権を与えると確認したわけではない。
- **最小修正:** 公開版は安定した証拠 ID とサニタイズ済み抜粋に置換し、元 URL 対応表は私的証拠へ分離する。公開対象に Git 履歴を含める場合は履歴にも残る点を確認し、承認された公開用 export/履歴方針を選ぶ。本監査では履歴を改変しない。併せて既知の LICENSE 未決定と支援 docs の配布・リンク先を公開ゲートとして維持する。
- **検証:** 記事だけでなく公開予定 tree 全体を検査し、公開予定履歴も別途確認する。公開リンクが第三者から閲覧可能で、証拠 ID と抜粋の対応が残ること。pattern 検査ゼロだけで秘密不存在を網羅的に保証しない。

### R03 — MAJOR（再現手順）: clean host の共有ライブラリ導入と依存閉包が読者任せ

- **箇所:** `docs/dependencies.md:13`, `docs/reproduction-procedure.md:9`, `docs/reproduction-procedure.md:19`, `docs/hardware-and-driver.md:20`。
- **根拠:** ホスト依存は libc/libstdc++/uuid/zlib/zstd/ncurses/tinfo 等の名前を挙げるが、対象 Ubuntu パッケージ・版・導入手順と完全な選択 ELF 閉包を提供していない。XRT は24.04向け DEB を抽出するだけなので依存解決は実行されない。hardware 文書も「appropriate Ubuntu kernel/firmware package」の導入を条件とするにとどまり、旧 kernel の取得を明示的に未解決としている。`verify.py` はファイル存在等を検査するが、完全な loader closure の合格を出すものではない。
- **影響:** 既存成功ホストに偶然揃っている host packages を隠れた前提にできる。R01 の archive pin だけを埋めても、クリーン環境で同じ loader 経路へ到達できる手順にはならない。
- **最小修正:** C++ 分岐に最低限必要なホストツールと実際の SONAME→Ubuntu package の対応、取得元・検証版、条件付き privileged install 手順、未解決依存で止まる preflight を追加する。kernel/firmware は historical exact pin が取得可能か、検証対象とする別 baseline かを明示する。SDK DEB の全依存を無差別に入れる処方にはしない。
- **検証:** pristine test host の package inventory と導入差分を保存し、既存 SDK/IRON ディレクトリを見えなくした状態でリンク・実 loader 記録を確認する。不足 SONAME の fixture が preflight を通過しないこと。実行を要する検証は今回の監査では行わない。

### R04 — MAJOR（保全・fail-closed）: build 出力の dangling symlink を既存と認識しない

- **箇所:** `scripts/build-probe.py:17`, `scripts/build-probe.py:43`, `scripts/build-probe.py:50`, `scripts/build-probe.py:51`。
- **根拠:** 入力の resolve/containment は検査する一方、出力 `inference-probe` / `probe-build.json` は `exists()` で判定する。dangling symlink は `exists()==False` なので両方の既存チェックを通過しうる。compiler の `-o`、receipt の `write_text()` はその symlink の先へ書ける。特に receipt が保存環境内の未存在ファイルを指す場合、事前の input containment とは無関係である。小さな隔離 fixture で `is_symlink()==True, exists()==False` を確認した。実 compiler 起動や保存環境への書込みによる再現はしていない。
- **影響:** 出力に stale/misplaced symlink がある場合、`.private-work` 内に限定し既存環境を保全する契約を満たさない。通常の空の staging で必ず発生する不具合とは言わない。
- **最小修正:** 出力 leaf を `lstat`/`lexists` 相当で検査し、symlink と予期しない既存物を拒否する。output parent の実パスも検査する。排他的な build lock と private temporary output を使い、既存宛先を置換しない形で完成物と receipt を確定する。
- **検証:** 外部の未存在 target を指す app/receipt symlink、既存通常ファイル、二重実行を device-free fixture で試し、compiler 起動前の拒否と target 不変を確認する。実 SDK の rebuild は不要。

### R05 — MINOR（証跡）: 記録した compiler と実際に使う compiler が異なりうる

- **箇所:** `scripts/build-probe.py:39`, `scripts/build-probe.py:50`。
- **根拠:** fingerprint の `g++ --version` は呼出元の環境/PATHを継承するが、build は `PATH=/usr/bin:/bin` で実行する。PATH先頭に別 compiler があると、記録・idempotence 判定が別 compiler の版に基づく。
- **最小修正:** compiler の絶対実パスを一度決め、version と build に同じ環境で渡す。実パスと、必要なら実ファイル hash も receipt に保存する。
- **検証:** 二種類の fake compiler を使う subprocess mock fixture で、version/query と build の選択が一致することを確認する。SDK link/device test は不要。

### R06 — MINOR（結果保全）: probe の出力拒否は排他的でない

- **箇所:** `src/inference-probe.cpp:66`, `src/inference-probe.cpp:126`。
- **根拠:** 出力不存在の確認から推論完了まで間があり、その後は通常の `ofstream` で作成する。同じ output を指定した二つの実行は両方が初回確認を通り、後の書込みが先の結果を切り詰めうる。launcher の事前 path containment は同一パス競合を防がない。
- **最小修正:** 出力を推論前に排他的に予約するか、実行ごとの一意な一時出力から no-replace で公開する。既存出力・symlink は拒否し、失敗時に途中結果を完了 record と扱わせない。
- **検証:** ORT/device に依存しない出力 writer fixture で、同一 destination の同時作成が一方だけ成功し、既存内容が不変であることを確認する。

## 証拠から支持できた点と、追加欠陥にしなかった点

- 指示書全936行を Library から読んだ。本文の17テーマと completeness audit は、必須範囲に証拠または明示的な未解決状態を割り当てている。未解決を記載したことと、独立再現が完了したことは別である。
- E025（memcpy source）、E035（historical C++ source）、E036（launcher）、E096/E097/E098（失敗・trace・成功）の private copy を inventory の SHA-256 と照合し、6件一致。原ログの対象行も確認した。
- E096 の398/2は失敗側にもある。E098の398/2、NPU subgraph 1、Inference/Quicktest PASSは原ログで確認できる。E035 は値の比較をしない。本文は API 完了、runtime attribution、数値正解、独立再現を混同していない。
- 失敗側は system coreutil の `openat=3`、成功側は local coreutil/core/driver_xdna の `calling init`。これを同じ観測や単一 ABI 原因の証明にしない説明は妥当。53/61名の比較は名前だけという制限も保持されている。因子分離実験を無理に実行して埋める必要はない。
- 保存された SDK/IRON interpreter probe は両方3.14.4。3.12未導入の判断範囲を限定し、3.14 import 失敗からC APIへ進んだ説明と整合する。「Python 3.12でSDK成功」は主張していない。
- 51.0 TOPS は収集担当の U 証拠整理経由。80.19 GB/s / 1849 µs / memcpy DMA warning は A 記述のみで原添付未回収、と本文が明記する。今回、元会話を独立に再取得して確認したとは扱わない。数値を ONNX 性能へ流用していない。
- IRONとSDKは別経路。SDK Peano21.0gitとIRON LLVM-AIE22の違い、cp310/cp314問題、source build未証明を保持している。C++成功をIRON再構築やSDK Python成功の代用にしていない。
- launcher の `env -i` と隔離 HOME/cache/tmp は隠れた環境依存を減らす設計である。ただし historical launcher は全環境を空にしていないため、この新経路が cold-cache で成功することは未検証。cache不足の具体的な故障を観測してはいないので、実在する確定バグとしては追加しない。
- staging の plan/apply 分離、hash mismatch 拒否、既存 destination の drift 拒否、archive traversal対策、timeout は適切な方向。fixture は synthetic なので real vendor archive の全 member、展開 cap、完全な依存を検証したものではない。
- 公開対象の限定 scan では会話リンク以外に、検索した個人ホームパス・代表的 token/key pattern の一致はなかった。全秘密不存在や第三者権利のクリアランスを保証する結果ではない。記事の一人称を均質化する文体修正は要求しない。

## 受入れを完了する最小の次工程

1. 別担当が R02/R04 を先に修正し、R05/R06を局所修正する。監査本文・scriptsの直接修正はこの担当ではしていない。
2. R01/R03を解消するか、取得不能部分を独立した新 baseline として分離する。C++を先に実証することは可能だが、IRON/Pythonの達成範囲を広げない。
3. 別途認可されたクリーンホストで、固定入力から展開・リンク・ロード・cold-cache Runを実行する。CPU/VitisAIに同じ保存入力を与え、モデルに妥当な事前定義の許容誤差で実出力を比較する。process exit、実選択library、driver/firmware、package差分、model/input hash、残存警告を保存する。
4. その証拠を得て初めて該当分岐の判定を更新する。一回のモデル比較を一般精度・性能・全ワークロード互換へ拡張しない。未回収のmemcpy原ログが埋まらなくても、歴史の不明点として残せる。

## 監査範囲・実施記録

- 監査対象 HEAD: `17f5a7406bee704654e60fdf90f8f935b47984b7`。開始時の working tree は clean。終了前にも同一 HEAD と clean を確認してから、この新規レビューだけを作成した。
- 技術基準: `be01af5f4071915f08f5978aecc8e5123cd2431b`。ここから対象 HEAD への差分は articles 配下5ファイルのみ。指定初稿本文 commit は `858b567bebf8547ff12d0d9eca8cf8a04b077903`。
- 読取対象: 本文、editorial review、関連再現・依存・SDK・IRON・Python・XRT・verification文書、manifest/phase2/static/inventory/XRT pins、staging/build/run/verify/probeコード、fixture、上記 private 原証拠。外部配布サービスの現在の取得可否は未実証。
- `python3 -I -B -m unittest discover -s tests -v`: **21/21 PASS**、unittest表示0.023秒。新規実機試験を意味しない。全 scripts の Python AST parse と Bash `-n`: PASS。
- private 原ログの再評価: E096 API success=false / NPU execution=false、E098 true / true。ともに数値検証・fresh-run証拠にはならない。
- 安全な dangling symlink fixture と tracked tree の限定公開情報検査を実施。compiler、vendor code、NPU/GPUは起動せず、再ビルド・インストール・download・OS設定変更・remote/push/公開・追加agent起動はしていない。
- 計測可能なのは上記テスト時間のみ。監査全体の正式な課金 usage、token数、Astra単独のクレジット消費はこのツール出力からは不明。料金や消費量は推算しない。
- アクセス拒否・承認待ち・結果不明の書込みはなし。指定IDとprivate-copy名の初回対応推測で3ファイルが見つからなかったが、inventoryの正規mappingで解消した。残る blocker は上記の成果物・検証未達であり、権限拒否ではない。
