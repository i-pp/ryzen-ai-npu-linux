# Article handoff for independent technical review

本文完成スナップショット: `858b567bebf8547ff12d0d9eca8cf8a04b077903`。
記事: [日本語初稿](../ryzen-ai-max-395-ubuntu-2604-npu-ja.md)。
本文SHA-256: `5b0a59824961b62ed8d5b1a4258751515312295f2d3eb7292f94a34d46f96f9f`。
確定した技術入力: `be01af5f4071915f08f5978aecc8e5123cd2431b`。

**初稿は独立監査へ渡せる状態。公開承認・最終技術合格・clean-install合格ではない。** 執筆者のセルフレビューと、予定されているAstraの独立レビューは別工程である。

## 変更範囲と読取資料

書込みは `articles/` だけ。既存SDK/MLIR-AIE、OS、技術docs/scripts/src/tests/artifactsへ変更していない。デバイス実行、vendor import、インストール、remote作成、push、公開、外部サービスへの原稿送信は行っていない。以下の初稿保存は生証拠の複製ではなく、新規執筆した文章の編集前版である。

- [初稿の編集前版](initial-draft-ja.md): SHA-256 `5d49c3b85c69e012140453ac9beeb54c82ba1c916066a686a0ccdc5774e7f14d`。
- [編集差分](changes.diff): 原因の言い切りと読者に不要な工程用語を修正。数値、引用ログ、コマンド、URL、未実施条件を削らず、意味をレビューした。
- [機械的確認](checks.json): 実際に実施した検査と未実施lintを区別。

必須指示書 `REQ-001` は全936行を読み、内容の再配布はしていない。全27技術docs、manifest全体、証拠inventory、phase2-evidence/validation、XRT package pins、起動wrapperと新probeのソースを確認した。重要な入口は [phase2 checkpoint](../../docs/phase2-checkpoint.md)、[原因解析](../../docs/xrt-investigation.md)、[完全性監査](../../docs/completeness-audit.md)、[再現手順](../../docs/reproduction-procedure.md)、[証拠索引](../../docs/evidence-index.md)、[chronology](../../docs/chronology.md) である。

元会話を直接全件読んだとは主張していない。会話由来の事項は、上記スナップショットにある収集担当のU/A/I区分付き整理を参照した。Uは当時のユーザー端末出力、Aは当時のassistant検索断片。記事に非公開会話URLは埋めていない。

## 適用した編集方針・スキルとツール

グローバルAGENTSと、既存 [policy provenance](../../docs/policy-provenance.md) の共通方針を確認した。`i-pp/ai-orchestration` の orchestration/policies/agents READMEもGitHubの読取機能で読み、許可範囲を広げる材料にはしていない。

既存zenn-articlesの `.pipeline/AUTHORING.md`、`.pipeline/EDITORIAL.md` とeditorial-policyを読んだ。適用範囲外の公開パイプラインをこのrepoへ導入せず、事実・数値・引用・コマンド・未検証条件を保持して差分を確認する考え方を再利用した。既存パイプラインの合格・承認を新たに得たとは主張しない。

`technical-writing` / `article-editor` / `zenn-publishing` の実体は、利用可能な全executor skillページと、既知のローカルskill・記事repoの限定探索では見つからなかった。未読の候補を実行したり、新規導入したりしていない。必須指示の「読める範囲で再利用」に従い、読めた共通編集資料を利用して初稿を完成した。

Libraryスキルは必須指示書の読取、write-like-meは文体参照の確認に使用。対象に合うユーザー原文の公開リンク付き執筆例は取得結果になく、ユーザー文体を学習済みとは扱っていない。一人称はログに対応する行為と今回の記録整理に限定し、体験・感情・動機を追加していない。

`noslop` と `textlint` はローカルコマンドが見つからずNOT_RUN。既存editorial policyもnoslop/slop-shieldの実体・版が未検証、testlint-jaの識別が未解決だった。別ツールへの読み替え、stubのPASS扱い、新規software導入、原稿の外部API送信はしていない。これらは公開前の編集工程で残る事項であり、今回の非公開初稿作成を止める理由にはしなかった。

## 17テーマと主要claim/evidence

Verifiedは直接読める記録・ソースの内容、Corroboratedは複数資料の整合、Inferredは説明仮説、Unverified/Unknownは不足が残る事項として使う。歴史的ログのVerifiedを、現在の再実行成功へ拡張しない。

| 章・必須テーマ | 本文で伝える内容 | 主な証拠 | 確度と制限 |
|---|---|---|---|
| 1 動機・目的 | UbuntuでNPU検出を越えてONNX推論へ進む | 指示書の目標、chronology、E096/E098 | 依頼と実行履歴に限定。感情・個人的背景を創作しない |
| 2 ハードウェア・OS | EVO-X3/MAX+395、26.04.1/7.0.0-42、二つのXRT | manifest、environment、E092–E094、保存probe | Verified snapshot。公式サポート/最低条件ではない。kernel38→42の必要性Unknown |
| 3 初期検出 | 既存amdxdna/render、XRT不在、FWロード | hardware-and-driver、chronology、U初期ログ、E089/E091 | 状態Verified/Corroborated。FW新規queryなし。namespace非表示をhost不在へ変換しない |
| 4 権限・memlock | 8 MiB/64 MiB/-11、EPERM、PAM/systemd、実効値 | U整理、E012/E014、memory-and-permissions | 強いCorroborated説明。root比較はuidも変更。1 GiBは必要最小値ではない |
| 5 XRT検証 | root/user検証、support archive、51.0 TOPS | U整理、E016、xrt-validation | 過去ユーザー出力が収集担当経由で回収。元local完全log/入力不足。ONNX性能・新測定ではない |
| 6 MLIR-AIE構築 | exact commit、guard、cp314/cp310、NumPy、wheelとsource buildの違い | E019–E028、P2-F001/F003/F006/F008、manifest | 現物Verified。full source build成功なし。wheel導入元/方法Unknown |
| 7 IRON | pyxrt可視性、SAXPY/reduce、memcpyの設計とDMA警告 | U整理、E025、P2-F007、P2-IRON-COMPARE、iron-execution | SAXPY/reduceはU。80.19/1849/PASS/DMAはAのみで一次log未回収。ソース条件を歴史的実行条件と同一視しない |
| 8 SDK導入 | archives、EULA、installer引数と処理、依存固定不足 | E029/E043/E050/E051/E052/E056/E059、sdk-installation | ソース動作Verified、完全なinstall transcriptと原アーカイブ照合は未回収 |
| 9 Python互換 | execstack失敗後ABI失敗、C++迂回 | U整理、P2-PY-ABI、元ZIP GNU_STACK、python-compatibility | 歴史的失敗＋静的裏付け。3.12導入成功・SDK3.14互換は主張しない |
| 10 ORT/C++ | C API、Env/logger順序、SDK Peano21、model IO、header | E033–E042、P2-HDR、P2-F004/F005、static-analysis | ソース/metadata Verified。歴史的full build command不足。静的output shapeを実測値にしない |
| 11 compile-only | compile/session成功後Run失敗、398/2でも未完了 | E096:385–386,740–752 | Verified歴史的log。EP登録・割当は推論成功条件の一部 |
| 12 原因調査 | system coreutilのopen、SONAME、53/61名、loader | E097:49、static-analysis、xrt-investigation | open/名前一致はVerified。初期化・ABI意味論は未証明。唯一原因Unknown |
| 13 working XRT | local base/npu/plugin、XILINX_XRT、探索順 | E036、E073–E079、P2-XRT-PLUGIN、E098 init | runtime-selection bundleをCorroborated remedyとする。一因子実験なし。system XRT維持 |
| 14 推論成功 | 398/2、1 subgraph、Inference/Quicktest PASS、残存警告 | E098:387,410–412,793–799,1151,1154,1227–1234、成功U整理、E035 | Verified log内容。独立device trace/別保存exit/numeric oracleなし。398/2を利用率・時間比にしない |
| 15 再現手順 | C++独立ルート、入力hash・新build・実行・比較の順 | reproduction-procedure R01–R11、verification-design、scripts/src | 手順・fixtureの存在。large hashes未回収、link/load/device/clean install未実施を明示 |
| 16 troubleshooting | 症状→確認対象、静的調査と実行の境界 | troubleshooting、runtime graph、上記失敗記録 | 対応する証拠から診断先を導く。自動修復を示さない |
| 17 限界・今後 | wheel/配布物/警告/数値/clean host/因果分離 | reproducibility-status、inference-verification、completeness-audit | 全て未達条件付き。完了の創作や成功範囲の拡大なし |

## 内部証拠から公開一次出典への接続

本文は内部IDだけを根拠に外部技術仕様を語らず、必要な箇所で次をリンクした。個別ホストでの結果は上表の内部証拠、一般仕様は公開一次出典という分担である。公式ページが手元の全構成をサポートするとは書いていない。

| 内部証拠 | 本文の公開参照 | 確認した範囲 |
|---|---|---|
| E050/E051、SDK/XRT archives | [AMD Linux instructions](https://ryzenai.docs.amd.com/en/main/linux.html) | 1.8のPython3.12と24.04向け配布物、正規取得入口。`en/1.8/` は取得できず、検索で確認できたmainを使用。mutableリンクを永続pin扱いしない |
| E019/E025、manifest source revision | [MLIR-AIE pinned tree](https://github.com/Xilinx/mlir-aie/tree/e28f6dc7e52fbb7b43f94b3693083c3f01a2387c) / [memcpy source](https://github.com/Xilinx/mlir-aie/blob/e28f6dc7e52fbb7b43f94b3693083c3f01a2387c/programming_examples/getting_started/00_memcpy/memcpy.py) | GitHub connectorでmemcpy sourceを読取。通常webのGitHub取得失敗をソース不存在の証拠にしない |
| P2-HDR | [ORT v1.27.0 header tree](https://github.com/microsoft/onnxruntime/tree/v1.27.0/include/onnxruntime/core/session) | phase2のblob一致記録、今回もC headerはGitHub読取で取得。巨大ヘッダーの全文を記事へ転載しない |
| E097、static ELF graph | [ld.so(8)](https://man7.org/linux/man-pages/man8/ld.so.8.html) | loader検索規則、RUNPATHの直接依存への適用。現在の特定SDK内部失敗分岐の証拠にはしない |
| P2-F001/F003、SDK WHEEL | [PyPA compatibility tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/) | interpreter/ABI/platformタグの意味。wheelメタデータと実装互換の違い |
| E012/E014、U process limits | [getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html) | 継承hard ceilingの一般仕様。個別のmmap失敗原因を仕様だけで確定しない |

公開記事内の標準パスは診断対象を指す。個人ホーム・実ホスト名・非公開会話URL・SDK binary bytesは含めていない。本文からの相対参照は記録repoで解決する。Zennへ実際に公開する工程では、この支援docsへの配布先とリンク解決、権利、最終編集、公開承認を別途確認する必要がある。

## 編集・検査結果

1. Cycle 1: 本文全体を技術docsと照合。原因の断定、過去log/現物/再構成手順の区別、Python経路、性能の根拠、stub警告、数値・clean-install条件をレビュー。原因説明を観測→仮説の順へ直し、読者向けでない「17テーマ」「新repo」表現等を修正した。差分は上記ファイルに保存。
2. Cycle 2: 修正版の意味と構造を確認。冒頭から結末まで、NPU検出→memlock→IRON→Python失敗→C API→compile-only→runtime選択→Run完了→次の検証条件がつながることを確認した。失敗の意味を省略してコマンド集へ短縮しない。追加のframework変更・際限のない書換えは行わない。

機械的確認は、既存markdown-it-pyによるメモリ内render/parse、YAML読取、17個のH2、12個のcode fence、21件の相対参照、Bash fence3件の `bash -n`、秘密・個人パス・会話URLの限定pattern scan、`git diff --check`。独自の日本語lintやZenn rendererは実行していない。parser成功はZenn表示の実機確認・人間向け文章品質の合格を証明しない。pattern検査0件も秘密不存在の網羅的保証ではない。

記事には実行結果を新たに作るコード変更がないため、既にphase2で通った21件のoffline fixturesやC++構文テストを再実行して、今回の変更の成功として数え直していない。

## Astraへ残す監査点

- XRT選択bundleを、確定した単一ABI原因へ言い換えていないか。成功stubとlookup診断を読んでも無害全般とは言っていないか。
- SDK3.12成功が未証明、両venv3.14.4、execstack後ABI失敗、C API迂回が崩れていないか。
- cp310 LLVM-AIEの再install不成立、wheel provenance、SDK large-input hashを、再現手順の実際の停止条件として残しているか。
- 51.0はU整理経由、80.19/1849はAのみ、398/2/1は原log、と証拠の強さを維持したか。
- API完了・runtime NPU報告・数値検証・clean-install合格を区別しているか。
- 本文にない感情やユーザーの個人的判断を加えていないか。一人称の記録整理と歴史的行為の読み分けに問題がないか。
- 支援docsへの相対参照はrepo上で有効だが、Zenn公開面では公開先を確定する工程が必要。公開可能という承認へ読み替えていないか。

執筆タスク自体へのdenial、pending approval、uncertain writeはない。外部lintの未実施、一次資料の未回収、実行・clean-installの未実施、公開面のリンク確定、権利確認、独立監査は残る。元環境へ変更してこれらを埋める行為は実施していない。

最終保存時の修正: 編集差分のcontext空行がGitのtrailing-whitespace検査に該当したため、同じraw→edited差分をcontextなしで再生成した。本文の再編集ではなく、本文commitとSHA-256は不変。最終的な全差分で `git diff --check` を通し直した。
