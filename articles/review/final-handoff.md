# CLI契約更新と添付用初稿の確認

技術入力: `c42f33ff7ed959e66af49ee1bc1680c2e6dd12c7`。
参照: [Astra指摘への技術修正記録](../../docs/reviews/astra-remediation.md)。
添付対象: [現行の日本語初稿](../ryzen-ai-max-395-ubuntu-2604-npu-ja.md)。
本文SHA-256: `5f5b28bfd8a7da6d778a709522f4fe934174cb7cbac13f6e26e9df39c3227571`、UTF-8、35316 bytes、310行。

変更は依頼された二点に限定した。本文第15章の旧個別ハッシュ引数を `--baseline "$NPU_BASELINE"` へ変更し、表・前後の説明もreviewed manifest契約へ合わせた。履歴復元用manifestが未完成でapplyできないこと、新規取得用は別baselineであることを維持している。編集レビューの必須指示書参照は公開用ID `REQ-001` に置換した。記事全体の書き直しや成功判定の更新はしていない。

## 旧稿と配布対象

`initial-draft-ja.md`、`changes.diff`、`editorial-review.md`、`checks.json`、`astra-followup.md` は各固定時点の編集履歴であり、現行CLIの手順書ではない。特に凍結した初稿コピーには廃止済みの引数がある。履歴資料の意味を変えないため、内容を最新CLIへ書き換えず、**添付・実行例・公開用記事として配布する対象から除外する**。今回の添付候補は上記の現行本文1ファイルだけである。

旧Git履歴には私的参照が残っている。今回のcurrent-tree修正でGit履歴が公開可能になったとは扱わない。承認済みの公開用export/履歴方針、LICENSE・権利・支援docsの配布先・Zennリンク確認は依然として別の公開ゲートである。

## 最終確認

2026-10-30 14:58:09 UTCに、既存ローカルツールだけで実施した。

- Markdown parse/render、YAML、H2 17章、code fence 12件、相対リンク22件: PASS。`published:false`、冒頭ChatGPT表示とtopicを維持。
- Bash fence3件の `bash -n`: 全てexit 0。記事中のPython CLI例の全オプションを現scriptのargparse定義と照合し一致。
- `stage-xrt.py` と `stage-cpp-sdk.py` のplanを実行し、両方exit 0 / PLAN。後者は履歴manifestのapply blockerを8件報告する。実展開・SDK import・compiler・デバイスは実行していない。
- `check-public-tree.py`: current treeの対象locatorパターンはPASS。`--history` はexit 1で履歴4commitに一致し、公開ゲートが閉じていることを確認。全面的な秘密不存在や公開権利の保証ではない。
- articles全体の個人パス・代表的tokenパターンは0件。記事差分の `git diff --check` はPASS。language lintの新規導入・再実行はしていない。

## native添付の状態

既存taskへMarkdownをnative fileとして直接uploadする機能は、公開されているツールの名称・説明を調べた範囲では利用できなかった。Library保存、Drive、Page等は別の保存先なので、既存task宛のuploadの代わりに利用していない。**uploadは未実施、fileIDは未発行**。承認拒否や結果不明のuploadはなく、迂回・新task作成・一般公開もしていない。上記の現行Markdownはローカル保存済みで、対応機能を持つ統括側からの添付に渡せる。

書込みはarticles内の本文・レビュー記録のみ。既存SDK/MLIR/OS、docs/scripts/tests/artifactsの変更、remote作成、push、公開は行っていない。クリーン環境での再現・実推論出力比較は未実施のままである。
