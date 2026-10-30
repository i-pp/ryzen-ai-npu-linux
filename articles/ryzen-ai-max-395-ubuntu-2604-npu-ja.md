---
title: "Ubuntu 26.04でRyzen AI MAX+ 395のNPUを動かすまで――IRONとC++推論の切り分け"
emoji: "🔬"
type: "tech"
topics: ["ryzenai", "ubuntu", "npu", "onnxruntime", "chatgpt"]
published: false
---

> この記事は、手元の実行記録と環境調査をもとに、ChatGPTの支援で構成・執筆・技術確認を進めた下書きです。過去の実行結果と、記事作成時に確認した状態を区別しています。独立したクリーンインストールでの再現と、推論出力の数値比較はまだ完了していません。

## NPUで、モデルの推論まで通したい

GMKtec EVO-X3のRyzen AI MAX+ 395にあるNPUを、Ubuntu 26.04から使いたい。今回の目標は、デバイス一覧に名前を出すところから進んで、ONNXモデルを実際に推論させることだった。

途中で、モデルのコンパイルとセッション作成は通るのに、推論だけが失敗する状態になった。そのときに出たのが、次のメッセージだ。

```text
XRT is not installed. This InferenceSession generates model binaries only.
```

しかし、XRTは入っていた。別の経路ではNPUのテストも進んでいる。「未インストール」をそのまま受け取ってパッケージを追加する前に、どの処理が通り、どの共有ライブラリが選ばれているのかを調べる必要があった。

最終的には、システムのXRT 2.21.75を残し、SDK用にローカル展開したXRT 2.25.37を選ぶ構成で、C++から呼んだONNX Runtimeの推論完了を確認できた。Python SDKの実行成功とは別の結果だ。ここでは、その区別に至るまでの失敗と調査を順にたどる。

## 最終的に残った環境は、公式手順と同じではない

調査対象を保存した時点の構成は次のとおりだった。表は動作環境の記録であり、この組み合わせ全体への公式サポートや、各バージョンが最低条件であることを示すものではない。

| 層 | 確認した構成 |
|---|---|
| ハードウェア | GMKtec EVO-X3、AMD Ryzen AI MAX+ 395 |
| OS・カーネル | Ubuntu 26.04.1 LTS、7.0.0-42-generic |
| NPU | PCI ID `1022:17f0`、カーネル内の `amdxdna` |
| ファームウェア | 起動ログのロード先と現物のリンクから1.1.2.65を裏付け |
| システムXRT | Ubuntuパッケージ `1:2.21.75+dfsg-4` |
| SDK用XRT | ローカル展開した2.25.37とXDNAユーザー空間プラグイン |
| MLIR-AIE / IRON | ソース `e28f6dc7e52fbb7b43f94b3693083c3f01a2387c`、Python 3.14.4 |
| Ryzen AI SDK | 1.8.0、既存SDK用venvもPython 3.14.4 |
| 成功したアプリ | C++からONNX Runtime 1.27.0のC APIを使用 |

SDKの[公式Linux手順](https://ryzenai.docs.amd.com/en/main/linux.html)にはPython 3.12と、24.04向けのXRTパッケージが登場する。私の環境では既存の二つのvenvがどちらも3.14.4だった。あとから記録を整理する際も、「SDKの要求が3.12」と「3.12で動作した」を混ぜないようにした。

最初の会話ログにはカーネル7.0.0-38、その後には42が現れる。更新と再起動の全手順は回収できていないため、38から42への更新が推論成功の必須条件だったとは判断できない。実際の状態と取得元は[環境記録](../docs/environment.md)、[manifest](../artifacts/manifest.json)に分けて残した。

## まず、ドライバを入れる前に現物を見る

初期の記録では、すでに `amdxdna` とrenderグループ所有のデバイスノードが存在し、実行ユーザーもrenderに所属していた。一方、ユーザー空間のXRTはまだなかった。ここを一括して「NPUドライバがない」と扱うと、動いているカーネル側まで変更してしまう。

私はPCI、ドライバ、ファームウェアの状態を分けて確認した。別のホストで同じ入口を調べるなら、次は状態を見るためのコマンドになる。

```bash
uname -r
lspci -nnk -d 1022:17f0
modinfo amdxdna
journalctl -k --no-pager -g 'amdxdna|amdnpu' -n 100
```

保存した起動ログにはドライバ0.7.0と、`amdnpu/17f0_11/npu_7.sbin` のロードが残っている。ディスク上では対応するリンクが1.1.2.65を指す。ただし、記事作成時にデバイスへ問い合わせてロード済みバージョンを再取得したわけではない。

調査用の実行環境からは `/dev/accel/accel0` や `/dev/dri/` が見えず、systemdのバスにも接続できなかった。これはホストの過去の実行ログとは観測範囲が違う。コンテナやエージェント内でノードが見えない場合も、まずホスト側のPCIと起動ログを照合したい。[ハードウェア確認手順](../docs/hardware-and-driver.md)には、ファイルの存在とロード成功の違いも記載した。

## メモリを64 MiB確保する前に、8 MiBの制限に当たった

UbuntuのXRTを入れても、すぐに一般ユーザーで検証が通ったわけではなかった。初期のシェルのmemlock上限は約8 MiB。会話から回収したユーザーの端末出力には、64 MiBのマッピングが `-11` で失敗した記録がある。

rootかつmemlock無制限での `xrt-smi examine` はデバイスを検出し、その後、一般ユーザーでも1 GiBの制限で検証が通った。この比較はmemlockを強く疑う根拠になる。ただし最初の比較はuidも変えており、memlockだけを変えた厳密な実験ではない。1 GiBがあらゆるワークロードの必要最小値だとも言えない。

途中では、自分のhard limitを128 MiBへ上げようとして `EPERM` になった。継承したhard limitを超える変更には制約がある。ここから先は同じ `prlimit` を繰り返すより、ログインとサービスのどこで制限が決まるのかを見る段階だった。[getrlimit(2)](https://man7.org/linux/man-pages/man2/getrlimit.2.html)にsoft/hard limitの関係が説明されている。

最終的なPAMの設定値は `1048576` KiB、systemd側は `LimitMEMLOCK=1G` だった。systemdのdrop-inは、最初に置いた場所が誤っており、後で次の場所へ修正している。

```text
/etc/systemd/system/user@.service.d/99-memlock.conf
```

設定ファイルを直したことと、稼働中のプロセスへ反映したことも別だった。`systemctl show` の表示、ユーザーマネージャーの実際の上限、そこから起動した子プロセスの上限が一致するとは限らない。シェルだけでなく、実際のプロセスの `/proc/<pid>/limits` も調べた。

```bash
ulimit -Sl
ulimit -Hl
prlimit --pid "$$" --memlock
```

権限についても、アカウントDBへのrender登録だけで終えず、実際のセッションでノードのACLとアクセスを確認する必要がある。当時はすでにrender所属だったので、「renderへ追加」が今回の修正だったとは書けない。PAMとsystemdそれぞれの設定例、反映確認、新規セッションが必要になる条件は[権限・memlock手順](../docs/memory-and-permissions.md)へまとめた。設定再読込だけで既存プロセスの上限が変わると見込んで、作業中のユーザーマネージャーを不用意に再起動しないようにしたい。

## XRTの検証が通っても、ONNX推論の証明にはならない

XRTの検証では、テスト用の `xrt_smi_strx.a` が不足する問題もあった。rootのホームと一般ユーザーのホームではキャッシュが別なので、一方に置けば他方でも使えるとは限らない。対象XRTのバージョンと実行ユーザーを揃える必要があった。

過去の会話から回収されたユーザーの端末出力では、rootのPerformanceモードと一般ユーザーのDefaultモードの両方で検証がPASSし、GEMMは51.0 TOPSと報告されていた。これは当時のXRT診断結果として扱っている。元のローカル出力ファイルと完全な入力条件は回収できておらず、この記事で再測定した値でもない。

この結果で確認できるのは、その診断が使ったカーネルとランタイム経路の動作だ。後で動かすONNXモデルのスループットや、Python SDKの互換性まで証明したことにはならない。診断の結果と、次のMLIR-AIE、さらにSDK推論の結果を分けて読むための最初の境界だった。[XRT検証記録](../docs/xrt-validation.md)には二つのモードの文脈と、将来測り直す際に保存する項目を残している。

## MLIR-AIEは、もう一つの開発環境だった

次に進めたのはMLIR-AIEとIRONだった。ONNXモデルをSDKへ渡す経路とは別に、NPU向けのプログラムを作り、コンパイルして実行する経路を確かめる工程になる。

保存したcheckoutは[Xilinx/mlir-aieの特定コミット](https://github.com/Xilinx/mlir-aie/tree/e28f6dc7e52fbb7b43f94b3693083c3f01a2387c)で、インストール済みのメタデータには次のバージョンが残っていた。

| 要素 | 観測したバージョン |
|---|---|
| Python | 3.14.4 |
| mlir-aie | `1.4.5.dev113+ge28f6dc` |
| llvm-aie | `22.0.0.2026102001+4f5df13d` |
| NumPy | 2.5.4 |

入口の `utils/env_install.sh` はPython 3.12を既定にするだけでなく、minor versionを明示的に検査していた。`PYTHON` を3.14へ向けるだけでは通らず、現物にはガードを3.14へ変更したローカル差分がある。これは今回の試行の記録であって、ガードを変えればネイティブ拡張まで互換になるという意味ではない。

記録を整理して、再インストールには別の問題が残ることも分かった。mlir-aieのWHEELタグは `cp314-cp314` だが、同じvenvにあるLLVM-AIEのタグは `cp310-cp310` だった。当時の `pip check` にもプラットフォーム警告が残っている。[wheelの互換タグ](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/)はPython・ABI・プラットフォームを表すので、この現物を通常のpipで再導入できるとは見込めない。どのファイルを、どの方法で入れたかの回収が必要だ。

NumPy 2.5.4も「入っていた版」として記録する。対象のmlir-aieメタデータではPython 3.12以上にNumPy `>=2.5.3,<3` を要求しており、2.5.4だけが解ではない。CMakeやNinjaは存在したが、完全なソースビルド成功のログはなく、記録したsubmoduleも未初期化だった。ここからフルビルド成功談を作ることはできない。[MLIR-AIE構築記録](../docs/mlir-aie-setup.md)ではwheelの取得元・ハッシュ・タグ不整合を、再構築前に解消する条件にしている。

## IRONの実行で、ハードウェア全体を疑う段階から進んだ

IRONでは `programming_examples/getting_started/00_memcpy/` を扱った。最初の実行では `CPUOnlyTensor` や `Unsupported device: npu` が出たが、システムPythonからはcp314の `pyxrt` をimportでき、venvからは見えていなかった。NPU自体の未対応と決める前に、venvのモジュール探索範囲を調べる必要があった。

現物のvenvには、システムのcp314用pyxrtへの単一のシンボリックリンクがある。全system site-packagesをまとめて取り込んだわけではない。正確な追加コマンドと時刻は回収できていないが、当時の見え方の差と現在のリンクが対応している。その後のユーザー端末ログには、SAXPYとvector_reduce_maxのPASSが残っている。

memcpyには証拠の差がある。過去のChatGPT応答の検索断片には、`PASS!`、80.19 GB/s、end-to-end 1849 µs、DMAバッファディスクリプタ再利用の警告を読み取った記述がある。しかし、元の添付・端末出力は回収できていない。私はこの二つの数値を、確認済みのベンチマーク結果として引用しない。

一方、[対象コミットのmemcpyソース](https://github.com/Xilinx/mlir-aie/blob/e28f6dc7e52fbb7b43f94b3693083c3f01a2387c/programming_examples/getting_started/00_memcpy/memcpy.py)からは、何を測る例なのかを読める。int32を16777216要素送り、同じ大きさの出力を受け取るので、帯域計算の分子は往復128 MiBになる。warmupは1回、測定は5回。帯域の分母はNPU側の平均時間で、Pythonから見たend-to-end時間とは違う。現在の比較関数は、許容誤差を省略すると `np.array_equal` で入出力を比較する。

このソースの意味と、失われた実行ログの内容も分けておきたい。DMA警告は正確な文面と発生元が未回収なので、単にPASSがあったから無害とは言えない。ディスクリプタの寿命と同期、繰り返し実行時のデータ一致は追試事項になる。

IRONでの実行成功は、プログラム転送・起動やシステムXRTからドライバへの経路を裏付け、「ハードウェアが一度も動かない」という説明を弱める。しかし、Vitis AI EPやONNX Runtimeの互換性はまだ試していない。[IRON記録](../docs/iron-execution.md)に、確認できたソース条件と未回収ログを分けて残した。

## Ryzen AI SDKを展開し、インストーラーの前提を読む

ONNXモデルを動かす側はRyzen AI SDK 1.8.0を使った。配布物には `LLM.tar.gz`、`deployment.tar.gz`、`onnxruntime.tar.gz`、`quicktest.tar.gz`、各種wheelが含まれる。後で必要になったPeanoも、SDK側のwheelに入っていた。

手元の `install_ryzen_ai.sh` を読むと、Python 3.12を明示的に呼ぶこと、`-a yes` がEULA同意に関わること、`-p` がvenv、`-c` が任意のC++展開先を指定することが分かる。既存ディレクトリを拒否するので、動いている環境へ何度でも上書きできるインストーラーではない。

処理にはvenv作成、uv・wheel・追加依存の導入、重複するORT系パッケージの整理、activateへのパス設定、アーカイブ展開が含まれていた。全依存の解決履歴までは固定できていない。また、この原名のスクリプトと元配布アーカイブ内のファイルとの完全一致も未確認なので、原名だけで「未改変のベンダー原本」とは判定していない。

SDKを入手する読者は、[AMD公式手順](https://ryzenai.docs.amd.com/en/main/linux.html)から認証・ライセンス条件を確認する必要がある。この記録リポジトリにはSDKバイナリやモデルを同梱せず、分かっている取得元とハッシュを[依存・配布物一覧](../docs/dependencies.md)に残した。SDK全体や一部の大きなアーカイブのハッシュは未回収で、ファイル名が同じだけでは再現用入力を確定できない。

## Pythonの版を置き換えても、ABIは置き換わらなかった

SDK用には、インストーラー中の四つの3.12参照を3.14へ変更した試行が残っている。しかし、PythonからONNX Runtimeをimportすると、まず実行可能スタックに関するエラーで止まった。当時のELFフラグ変更の後は、別のエラーが現れた。

```text
undefined symbol: _PyThreadState_UncheckedGet
```

ここで起きているのは二段階の失敗だった。スタック属性の問題を越えても、CPythonのネイティブABIの問題が残った。静的調査でも、元wheel内のバインディングはGNU_STACKがRWE、現在のバインディングはRWであり、現在のバインディングが要求するこのシンボルはPython 3.14本体の動的エクスポートには見つからなかった。この記事の調査ではELFを書き換えていない。

wheelの名前も十分な保証ではなかった。ORTのwheelは `py3-none-linux_x86_64` と名乗る一方でネイティブの `.so` を含み、VOEには `cpython-312` を名前に持つ拡張が入っていた。「pipに入った」と「importできる」は違う。

当時のAPTではPython 3.12の候補が見つからず、その後に3.12を用意してSDK Pythonで成功した記録もない。既存venvは3.14.4のままだ。そこで私はPythonバインディングを通らず、C++からORTのC APIを呼ぶ経路へ進んだ。これはPython 3.14対応の修正成功ではなく、失敗しているAPI境界を通らない方法だった。3.12を別prefixやコンテナへ用意する案は、今も独立した未検証の分岐として[Python互換性記録](../docs/python-compatibility.md)に残っている。

## C++からC APIを呼び、コンパイラーの依存も揃える

C++側ではONNX Runtime 1.27.0のC APIを使った。C++ラッパーAPIを使ったという意味ではない。対応する[公式v1.27.0ヘッダー](https://github.com/microsoft/onnxruntime/tree/v1.27.0/include/onnxruntime/core/session)を揃え、`onnxruntime_c_api.h` に加えて、それが参照する `onnxruntime_ep_c_api.h` も用意した。保存した二つのヘッダーは、公式ファイルのGit blob IDと一致している。

ヘッダーが揃うとprovider列挙へ進んだが、EP登録ではloggerの初期化順序に当たった。`OrtEnv` を作ってからVitisAIをセッションオプションへ登録する。その先ではコンパイラー側の依存不足、さらに `libpeano-lib.so.21.0git` の不足が出た。

必要だったPeanoはSDKの `llvm_aie` wheel中の `lnx64.o/tools/peano/lib` にあった。IRONで使ったLLVM-AIE 22と、SDKのPeano 21.0gitは同じものとして扱えない。ELFを調べても、SDKの `libxcompiler-mlir-e2e.so` はこの21.0gitを直接要求していた。アプリを `-lonnxruntime` でリンクできたことだけでは、後からロードされるEPとコンパイラーの依存は揃わない。

モデルはSDK quicktestの `test_model.onnx`。静的メタデータは入力float32 `[batch_size,3,32,32]`、出力float32 `[batch_size,10]` で、当時のC++アプリはbatch=1を選び、seed 42の乱数入力を渡していた。モデルのSHA-256とAPI呼び出しの構成は[ORT統合記録](../docs/onnxruntime-integration.md)に記載した。

元の完全なコンパイルコマンドは回収できていない。新しい検証プログラムのビルドコマンドは別に再構成し、過去にそのまま実行したコマンドとは区別した。元バイナリには元SDKへの絶対RUNPATHもあるため、別のマシンへコピーすれば動く実行ファイルとは考えない。

## セッション作成のPASSの後で、Runが失敗した

ヘッダーとコンパイラーの依存を揃えると、EP登録とモデルコンパイルは進んだ。保存した失敗ログE096には、次の行がある。ここでは時刻などを省いて抜粋した。

```text
ONNX Runtime: 1.27.0
Vitis AI EP registration: PASS
INFO: [VAIP-VAIML-CUSTOMOP] XRT is not installed. This InferenceSession generates model binaries only. The session handle can not be used for inference run.
Skipping execution in compile-only mode
```

その後の `Run` は、`output_DequantizeLinear` で `the ort_value must contain a constructed tensor or sparse tensor` を含むエラーになった。一方、同じログには `ONNX session creation: PASS` も残っている。

セッションを作れることと、実行用テンソルが構築されて推論が完了することは別だった。失敗ログにもNPUへ398演算子、VITIS_EP_CPUへ2演算子という割当結果がある。その数字だけを拾っていたら、コンパイル結果を実行成功と読み違えていた。[抜粋と原ログの行番号](../docs/evidence-excerpts.md)では、この失敗から成功までを対で参照できる。

## 「XRT未導入」を、ライブラリの選択まで掘る

XRTのパッケージは存在し、別経路のテストも進んでいる。そこで失敗したプロセスが何を開いたかを調べた。保存したstrace E097には次の行があった。

```text
openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/libxrt_coreutil.so.2", O_RDONLY|O_CLOEXEC) = 3
```

これで言えるのは、システム側のファイルを開くことには成功した、ということだ。XRT全体が初期化されたことや、SDKとABI互換だったことまでは分からない。「ファイルがない」と「SDKが実行可能な状態として使えていない」を分けて調べる材料になった。

`readelf` で依存、SONAME、RPATH/RUNPATHを調べ、XRTの参照シンボル名も比べた。システム版とローカル版のcoreutilは、どちらもSONAMEが `libxrt_coreutil.so.2`。調べた範囲では、EPが直接参照するXRT系53名、Dynamic Dispatchの61名は両方に存在した。

そのため、「2.21には必要なシンボルが一つ欠けていた」とは結論できない。この検査は名前の比較で、シンボルバージョン、C++オブジェクトのレイアウト、関数の意味、動的検索、プラグインの初期化までは調べていない。名前が揃ったこともABI互換の証明にはならない。

探索パスにも注意が必要だった。Vitis AI EPにはcoreutilへの直接依存がある一方、EP自身にRPATH/RUNPATHはなかった。[動的ローダーの仕様](https://man7.org/linux/man-pages/man8/ld.so.8.html)ではRUNPATHは直接の依存に適用され、子の依存全体へ継承されるものではない。アプリのリンク情報や `ldd` の一枚だけでは、後からロードされる依存まで確定できない。

現時点で確かめられるのは、後述の構成変更をした試行で推論完了へ進んだことだ。SDKのランタイム選択・初期化が関わると考えると結果を説明できるが、特定のABI不一致や環境変数一つを唯一の原因として確定するには、条件を固定した比較と、SDK内部の失敗分岐の特定が足りない。[XRT原因解析](../docs/xrt-investigation.md)には観測と仮説を対応させた。

## システムXRTを残して、SDK用のXRTを選ぶ

成功した試行では、AMDの `RAI_1.8_Linux_NPU_XRT.zip` に含まれるbase、npu、XDNA pluginのDEBをローカルへ展開した。システムのdpkgへインストールして置き換える方法は取っていない。

起動時には、`XILINX_XRT` をそのローカルルートへ向け、`LD_LIBRARY_PATH` を「ローカルXRTのlib → SDKのORTライブラリ → SDKのPeano」の順に限定した。元の起動スクリプトは、呼び出し元の古い `LD_LIBRARY_PATH` を後ろに足していない。設定の対応は次のようになる。

```text
XILINX_XRT = ローカル展開先/opt/xilinx/xrt
LD_LIBRARY_PATH = ローカルXRT/lib:SDKのORT/lib:SDKのPeano
```

成功ログE098では、ローカルのcoreutil、core、`libxrt_driver_xdna.so.2` の初期化が確認できた。失敗側のstraceによる「open」と、成功側のローダーログによる「init」も同じ観測ではない。それでも、設定したパスと実際に選ばれたライブラリを結び付ける証拠になる。

この変更ではXRT本体、プラグイン、環境変数、探索順がまとめて変わった。「XRTを新しくしたら直った」という実用上の手掛かりは得られたが、各要因の寄与は分離できていない。また、24.04向けパッケージのローカル展開が、26.04上の依存を登録・解決してくれるわけでもない。別ホストでは実際の共有ライブラリ依存を確認する必要がある。

IRON側はシステムXRT、SDK C++側はローカルXRT、と起動プロセスごとに選択する。二つの経路とPeanoの違いは[ランタイム構成図](../docs/runtime-architecture.md)、取得物のハッシュは[XRTパッケージ記録](../artifacts/xrt-packages.json)へまとめた。元の成功環境と起動スクリプトは変更せず保存している。

## 推論は完了した。ただし、PASSが検査した内容を読む

保存した成功ログE098には、次の割当と実行報告がある。

```text
   NPU   398
VITIS_EP_CPU     2
```

```text
   NPU     1
Actually running on NPU      1
```

さらに、アプリは `Run` を呼び、次の出力まで到達した。

```text
ONNX Runtime: 1.27.0
Vitis AI EP registration: PASS
ONNX session creation: PASS
Output count: 1
Running inference...
Inference: PASS
Output[0]: output
Quicktest: PASS
```

失敗側と違い、今回はAPIの推論完了と、ランタイムによるNPUサブグラフ1個の実行報告が両方ある。これを今回の到達点にした。独立したハードウェアトレースを取得したという意味ではなく、元プロセスの終了コードも別ファイルとしては残っていない。

398対2は演算子の割当数で、NPU使用率99.5%や処理時間の比率ではない。静的な元モデルのトップレベルノード数は386で、コンパイラー変換後の表現とは数が違う。CPU側の処理も残っている。

成功時にも警告・診断は残った。会話ログには `No driver detection supported`、ローダーログには `compile_onnx_model_vitisai_ep_v3` と `profiler_start` / `profiler_stop` のsymbol lookup診断がある。そのため、driver-detection stubがあるから実行不能だという途中の仮説は採用できない。今回のプロセスの完了を妨げなかったことは分かるが、関連機能すべてへの影響や無害性を確認したわけではない。

もう一つ、元のquicktestは出力数と名前を表示するだけで、値を参照結果と比較していなかった。**推論完了のPASSを、数値精度検証のPASSへ読み替えることはできない。** 記録整理の工程では、同一モデル・同一入力でCPUとVitisAIの出力を保存する新しいprobeと比較器を用意した。ただし、実データでの比較は未実行だ。[推論検証の段階](../docs/inference-verification.md)では、API完了・NPU実行報告・数値比較を別々に判定している。

## 別のUbuntuへ持っていくなら、C++経路から始める

ここまでの履歴を、そのまま再実行する必要はない。新しいホストでC++推論を試す場合、Python 3.14への置換やexecstack修正を再現する理由はないし、独立したIRON環境の未解決wheelを先に解く必要もない。

ただし、今回の手順はクリーンインストールで実証済みのレシピにはまだなっていない。[再現手順](../docs/reproduction-procedure.md)では、各工程を「必須」「条件付き」「診断」「任意」「過去の失敗」に分け、次の順序と停止条件を置いている。

| 順序 | 新しい検証ホストで行うこと | 次へ進む条件 |
|---|---|---|
| 1 | OS・PCI・amdxdna・起動ファームウェアを記録 | NPUへのバインドと初期化を確認 |
| 2 | 実行ユーザーのノード権限と実効memlockを確認 | 実際のシェル・サービスからアクセスできる |
| 3 | ライセンスを確認してSDKを取得し、C++用入力を固定 | 取得物をレビュー済みのbaseline manifestへ固定 |
| 4 | XRTのbase/npu/pluginを別領域へ展開 | 記録したハッシュと展開結果が一致 |
| 5 | v1.27.0ヘッダーで新probeをビルド | 構文確認に加え、リンクとロードを新たに確認 |
| 6 | CPUとVitisAIで同一の保存入力を実行 | 終了状態・選択ライブラリ・Run完了・NPU報告を保存 |
| 7 | 出力型・形状・有限性・値を比較 | 事前に決めた許容誤差を満たす |

3のORTアーカイブとSDK Peano wheelの完全ハッシュは、今の記録では未回収だ。新しく取得したファイルのハッシュをmanifestへ記録すれば、その記録とファイルの一致は確認できる。しかし、それだけでは過去に成功した配布物との同一性は確認できない。同一構成の復元には、成功時の取得元・版・完全ハッシュ・配布物内の配置を固定した記録が必要で、今はその入力が揃っていない。新規取得物で追試する場合は別のbaseline IDを付け、取得物と実行結果を保存する。成功しても、歴史的構成をそのまま復元できたとは扱わない。

入力を固定した後にも、クリーンホストの依存が残る。libc、libstdc++、uuid、zlib、zstd、ncurses、tinfoなどの名前は挙げられるが、必要なSONAMEからUbuntuパッケージ・検証版・導入手順への対応と、実際に選ばれる共有ライブラリの依存全体は、まだ確定していない。保存ホストに揃っていたパッケージを暗黙の前提にはできない。ファイル存在検査のPASSだけで終えず、別ホストの導入差分と実際のローダー記録を確認する工程が要る。元のカーネル・ファームウェアを取得できず別の版を選ぶなら、それも新しいbaselineの条件として記録する。

SDK Pythonを選ぶなら別途3.12の用意、IRONを選ぶならwheelの出所とcp310/cp314問題の解消が加わる。

この記録リポジトリの補助スクリプトは、基本的にplan表示から始まる。例えば、必要な配布物を正規に取得し、変数にその入力ディレクトリを設定した新しいcheckoutでは、次のコマンドで展開計画を読む。`NPU_BASELINE` には履歴復元用manifest、または別のIDを持つレビュー済み新規取得用manifestを指定する。[baselineの選び方](../docs/baseline-policy.md)に従って記録を固定し、不一致のたびに期待ハッシュを書き換えない。履歴復元用は入力が不足しているため、現時点では適用できない。

```bash
python3 -I -B scripts/stage-xrt.py --packages "$XRT_PACKAGES"
python3 -I -B scripts/stage-cpp-sdk.py --archives "$SDK_ARCHIVES" --headers "$NPU_HEADERS" \
  --baseline "$NPU_BASELINE"
```

これは展開・実行の成功例ではない。配置を適用する段階には `--apply`、SDKにはライセンス確認の指定も必要になる。新probeの実行は別途、隔離した作業領域と明示的な実行指定を要求し、1試行180秒に制限してログを保存する。既存のSDKやMLIR-AIEを実行・改変して確かめ直すためのスクリプトにはしていない。

オフラインの検証スクリプトは、`0=PASS`、`1=FAILあり`、`2=未実施・証拠不足のSKIPあり` を返す。成功した昔のログを読み込んでも、新規実行と数値比較がなければ全体はSKIPになる。この区別を消してしまうと、履歴の確認がいつの間にか再現成功になってしまう。

## 同じ症状に当たったとき、次に見る場所

今回の失敗を、次の確認箇所まで含めて並べるとこうなる。設定を変更する前に、該当する層の実測値を残すための表だ。

| 症状 | 次に確認するもの |
|---|---|
| ホストにはNPUがあるのにノードが見えない | 実行namespaceとホスト側PCI・起動ログ・ACLの違い |
| 64 MiBのマッピングが失敗する | 実際のプロセスのsoft/hard memlock、uid、継承元 |
| hard limitを上げるとEPERM | ログイン・ユーザーマネージャー・子プロセスの制限 |
| XRT検証のサポートアーカイブがない | XRTの版と、実行したユーザーのキャッシュ |
| IRONでCPUOnlyTensor / Unsupported device | そのvenvから、対応ABIのpyxrtが見えるか |
| LLVM-AIEのplatform警告 | 実際のWHEELタグとPython ABI、導入元 |
| SDK Pythonのexecstack / private symbolエラー | ELF属性とCPython ABIを分ける。ガード変更で互換と見なさない |
| EP登録でloggerエラー | `OrtEnv` 作成と登録の順序 |
| Peanoが見つからない | SDKコンパイラーの `DT_NEEDED` とSDK Peanoの探索先 |
| XRT導入済みなのにcompile-only | そのプロセスが開いたcoreutil、プラグイン、探索パスと初期化 |
| 演算子割当はあるが推論結果がない | `Run` の完了・エラーと、出力値の検査を別々に確認 |

`readelf` と `nm` による静的調査、保存済みログの検査、`LD_DEBUG` やstraceを付けた実行も分けて扱う。後者は実際にアプリを動かすため、元環境の保存作業のつもりで実行しない。[詳細なトラブルシューティング](../docs/troubleshooting.md)と[検証スクリプトの契約](../docs/verification-design.md)に、各確認がどこまでを判定するかを残した。

## 次に必要なのは、同じ結果を別の環境と実出力で確かめること

今回、保存したC++の失敗ログと成功ログからは、コンパイルのみの状態から、ローカルXRTを選んだ構成での推論完了までを追える。IRONの結果も含めて、ハードウェア、Python、コンパイラー、実行時ライブラリを一つずつ分けて扱う材料が得られた。

残っている課題は具体的だ。MLIR-AIE/LLVM-AIE wheelの取得元とタグ不整合、SDKの大きな入力アーカイブのハッシュ、元インストーラーとの照合、失われたmemcpy出力とDMA警告を回収する。XRTの内部原因を確定したいなら、モデルやキャッシュなどを固定してランタイム構成の要因を分離する実験も要る。

数値検証には、同じモデルと入力のバイト列をCPU/VitisAIへ渡し、実際の出力を比較する工程が残る。比較器の条件は `abs(npu-cpu) <= atol + rtol*abs(cpu)` だが、この量子化モデルに許容する値を事前に決める必要がある。比較器のオフラインテストが通ったことは、モデルの精度が通ったことではない。CPU参照も同じベンダーORTの別実行経路なので、それだけで独立した正解データにはならない。

私は動いた元環境を残したまま、取得物を固定した別のUbuntu環境で、リンク・ロード・Run・数値比較を順に確認できる形へ記録を移した。現時点の未達項目は[再現性の状態](../docs/reproducibility-status.md)、各工程の証拠と欠落は[完全性監査](../docs/completeness-audit.md)、保存ログのIDとハッシュは[証拠索引](../docs/evidence-index.md)から追える。次の追試では、`Quicktest: PASS` の先に、比較可能な実出力を残したい。
