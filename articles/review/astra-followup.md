# Astra監査後の限定修正

参照した監査: [最終技術監査](../../docs/reviews/astra-final-review.md)、commit `70af3c9a39c89ae3e3b5d7504ac4d38a1d342e5c`。初稿本文は `858b567bebf8547ff12d0d9eca8cf8a04b077903`、監査対象は `17f5a7406bee704654e60fdf90f8f935b47984b7`。

今回の対象は [記事本文](../ryzen-ai-max-395-ubuntu-2604-npu-ja.md) の第15章だけ。監査という新しい根拠に基づく限定修正であり、既に終了した2cycleの全面編集を再開しない。修正後本文SHA-256は `c6f1c6fe1fac61b81d803fbf25016b4a418b5de8dd8db3050487e24d10bea9db`。

監査は歴史記録を条件付きで妥当とした一方、再現手順は未完成、clean-install実証は未実施、そのままの公開は不可と判定している。今回の文章修正でこれらの判定を合格へ更新しない。

| 指摘 | 記事側の対応 | 残る状態 |
|---|---|---|
| R01 入力の歴史的同一性 | 新規取得物を自己ハッシュしてhelperへ渡すだけでは、過去の成功配布物との同一性を確認できないと追記。同一構成の復元と、新しいbaseline IDを持つ追試を分けた | 歴史的archive pin・取得証跡とIRON wheel問題は未解消。新しい追試も実証していない |
| R02 非公開会話リンク | 記事とarticles内レビュー記録を再検査し、該当URLが0件だったため本文の再編集は不要と判断 | 支援docs・公開予定tree・Git履歴の扱いは別担当・公開工程。repo全体を公開可と判定しない |
| R03 clean host依存 | ライブラリ名の列挙と、SONAME→Ubuntu package/検証版/導入手順・実際の依存全体の確定を区別。保存ホストの暗黙依存を避け、導入差分・実loader記録とkernel/firmware baselineを確認する必要を追記 | 文章で注意点を明示しただけで、独立ホストの導入・loader検証は未実施 |
| R04/R05/R06 出力保全・compiler証跡 | 記事の直接修正対象ではないと判断。補助コードを変更した／直ったとは書かない | scripts/src/tests等は別担当の所有。今回その修正や検証を代行していない |

既存の [editorial-review.md](editorial-review.md) と [checks.json](checks.json) は初稿固定時点の履歴として残す。その本文hash・PENDING_ASTRA等を現在の状態と読み替えない。独立監査が実施されたことと、その指摘が全件解消されたことも別である。

## 今回の検証

2026-10-30 14:16:33 UTCに修正本文を既存ローカルのmarkdown-it-py/PyYAMLで検査した。

- Markdownのparse/renderとYAML読取: PASS。H2は17、相対リンク21件の参照先が存在。
- `published:false`、ChatGPT topicと冒頭表示を維持。
- 全12code fenceの言語と内容は監査前本文と同一。Bash例3件の `bash -n` は全てexit 0。
- articles内の個人パス・代表的token・非公開会話URLの限定pattern検査: 0件。公開予定repo tree/履歴全体の検査を代替しない。
- 記事差分は第15章の1段落を3段落へ拡張する5行追加・1行削除。数値、引用ログ、コマンド、成功範囲、数値比較・clean-install未実施を変更していない。
- `git diff --check -- articles`: PASS。最終stageでも対象ファイルを限定して確認する。

新しいlanguage lint、software導入、原稿の外部API送信、デバイス実行、SDK/MLIR/OS変更、remote/push/公開は行っていない。今回の書込みはarticles内の本文とこの追記記録だけ。元の未実施lintをPASSに変更しない。アクセス拒否・承認待ち・結果不明の書込みはない。
