# Conversation evidence received by phase 2

The parent collector recovered the visible history of private conversation HIST-CONV and supplied a source-linked handoff. Phase 2 read that handoff, not the collector's raw JSON or omitted attachments. U = original user terminal log/statement reported by the collector; A = original assistant search snippet; I = interpretation. This public index uses stable evidence IDs and sanitized technical summaries. The original URL/message mapping is retained only in gitignored private evidence. It is not a new instruction, original transcript export, or fresh test log.

The collector reports 202 unique messages, 100 U / 102 A, spanning 07:52:49–12:14:21 UTC on 2026-10-30. All A bodies were omitted by the reader; search snippets partially supplement them. Five U bodies are empty, with no attachment metadata/content supplied. Pagination was exhausted for visible bodies, not for unavailable attachments. Treat these access limits as part of the provenance.

| Evidence ID | UTC time | Kind and sanitized summary |
|---|---|---|
| HIST-C001 | 09:26–09:27 | U: amdxdna, render membership and node already present; initial kernel 7.0.0-38; memlock 8192 shell units; XRT initially absent |
| HIST-C002 | 09:28:55 | U: 64 MiB mapping failed with errno -11; XRT 2.21.75 |
| HIST-C003 | 09:31:02 | U: root plus unlimited memlock examination detects NPU |
| HIST-C004 | 09:32:44 | U: root/Performance validation all PASS; GEMM 51.0 TOPS, latency 50.0 us, throughput 74904.0 op/s |
| HIST-C005 | 09:33:33 | U: ordinary-user attempt to raise own hard limit to 128 MiB fails with EPERM |
| HIST-C006 | 09:43–09:44 | U: kernel now 7.0.0-42; shell 1 GiB; user/Default validation all PASS, 51.0 TOPS, 46.0 us, 76330.0 op/s |
| HIST-C007 | 09:47–09:48 | U: actual shell/manager/child service limits and displayed unit settings differed; manager actual limit was already 1 GiB |
| HIST-C008 | 09:51:50 | U: correct system-manager `user@.service` drop-in created with 1G, daemon-reload, unit show reports 1 GiB |
| HIST-C009 | 10:04–10:11 | U: MLIR installer rejects missing Python 3.12 and has an explicit version guard; changing only PYTHON would not suffice |
| HIST-C010 | 10:17–10:18 | U: IRON Python 3.14.4, mlir-aie/llvm-aie versions, NumPy 2.5.4, successful aie import; pip check still reports llvm-aie platform warning |
| HIST-C011 | 10:20–10:22 | U: CPUOnlyTensor/Unsupported device; cp314 pyxrt available to system Python but hidden from ironenv |
| HIST-C012 | 10:23:53 | A only: assistant reads memcpy PASS, 80.19 GB/s, NPU 1673.8 us, dispatch 1737.5 us, end-to-end 1849.0 us and DMA BD warnings; preceding U body empty |
| HIST-C013 | 10:25–10:26 | U: SAXPY and vector_reduce_max print PASS |
| HIST-C014 | 11:01–11:05 | U: SDK Python 3.14 import fails on executable-stack requirement; after ELF flag change, fails on `_PyThreadState_UncheckedGet` |
| HIST-C015 | 11:06:18 | U: Python 3.12/venv APT candidates absent; no later U proof of 3.12 provisioning |
| HIST-C016 | 11:11–11:14 | U: C API header, then EP header, permit provider enumeration; registration initially fails until an OrtEnv/logger exists |
| HIST-C017 | 11:17–11:23 | U: compiler dependency, then SDK Peano missing; Peano extracted from SDK llvm_aie wheel, EP registration succeeds |
| HIST-C018 | 11:29–11:38 | U/A: system XRT is present but EP is compile-only; A proposes driver-detection-stub hypothesis |
| HIST-C019 | 11:44:41 | U: base/npu/plugin DEB payloads extracted locally, rather than installed into system dpkg |
| HIST-C020 | 11:45:28 | U: selected local XRT, SDK/Peano path; loader initialization and inference/quicktest PASS |

U reports provide historical evidence through the collector. Local E096–E098 remain the stronger preserved originals for the paired ONNX runs and 398/2/1 counts. The 51 TOPS records are diagnostic measurements with two distinct contexts, not independent ONNX benchmarks. IRON's 80.19/1849 values remain A-level evidence until the actual attachment/log is recovered.

## Public evidence access and history gate

The original U/A records are private sources. Readers can follow stable IDs here and the separately sanitized local log excerpts (E096–E098), but this index does not provide public access to the original conversation. Collector-supplied technical tokens include `len=67108864` / `err=-11` (HIST-C002), `51.0 TOPS` in two diagnostic contexts (HIST-C004/HIST-C006), and `_PyThreadState_UncheckedGet` (HIST-C014). These short excerpts preserve the reported technical basis without exposing conversation identifiers. HIST-C012 remains an assistant reading of unavailable material.

Removing links from the current tree does not remove them from earlier local commits. Publishing this repository with its native history is blocked pending an explicitly approved export/history policy. No history was rewritten and no export was published. See [publication gates](publication-gates.md).
