# NEW CHAT HANDOFF — Samsung A14 5G SM-A146P stock 6.6.89 + KernelSU Next
**Prepared 2026-10-16 (Sydney). Intended for a successor ChatGPT conversation.**

## Read this first / deliverable
Continue **hands-on engineering**, not just advice, for user's Samsung Galaxy A14 5G `SM-A146P` running firmware `A146PXXUHEZB1`, stock Android 15 ARM64/4 KB Linux `6.6.89-android15-8-abA146PXXUHEZB1-4k`, SoC **MediaTek MT6833 / Dimensity 700**, codename `a14xm`.

Two equal goals:
1. Obtain a **Samsung-stock 6.6.89-compatible KernelSU Next loadable `.ko`**, independent of Physwizz, using Samsung GPL + Android GKI source and validating against **actual stock boot.img BTF, IKCONFIG, symbols, module CRCs**, and on-device behavior.
2. Investigate eventual **genuine Samsung stock firmware with LOCKED bootloader**, keeping original OEM-signed `boot.img` and `init_boot.img`, with separately proven privileged late module loader. No viable A146P exploit/profile has been established; never imply verified feasibility. Separately migrate user's currently unlocked phone from FolkPatch/APatch-like root to *independent boot-persistent* KernelSU Next on known-working Physwizz 6.6.89 if safely possible.

**Current result: no stock 6.6.89-validated `.ko`, no boot-tested reconstructed stock kernel, and no locked-BL root/loading method.** Don't flash experimental images, tell user to relock BL, or promise success without proof. User strongly insists **no Physwizz source in final independent stock kernel**; using it as a comparative reference is permitted.

## GitHub worksite & tooling
- Repository: https://github.com/wiredroid/Patch-Recovery
- Work **ONLY** on branch `a146p-ksunext-stock-build`, leave `main` untouched: https://github.com/wiredroid/Patch-Recovery/tree/a146p-ksunext-stock-build
- Last research commit before the handoff: `52b0bc4a7f2d470c2ac2740cbd3df0982cfcbd88`; the handoff document was committed afterward. Verify current branch HEAD before edits.
- Connected GitHub app via available tools named `mcp__GitHub__fetch`, `fetch_file`, `update_file`, `create_file`, `fetch_workflow_run_jobs`, `fetch_workflow_job_logs`, and `fetch_workflow_run_artifacts` (available under `functions.exec`). Prefer connector for repo files, CI and workflows.
- GitHub Actions workflow definitions in `.github/workflows/a146p-*.yml`; current stock compilation `.github/workflows/a146p-stock-6.6.89-abi-build.yml`. Use logs *and* attached diagnostics; success of YAML workflow is not source/ABI proof.

## User-provided original binaries — IMMUTABLE reference
Original user-uploaded `boot.img` (32 MiB) and `init_boot.img` (8 MiB) are present in the prior conversation's Files/Library. If not accessible in new chat, request reattachment or use Files Library; do not invent local sandbox paths.

| Original OEM file | Exact SHA-256 |
| --- | --- |
| `boot.img` | `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9` |
| `init_boot.img` | `a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976` |

These hashes are **byte identity targets**. Rebuilding equivalent C or embedding KernelSU into boot/init_boot **cannot** preserve the exact original hashes. Stock locked verified boot requires original correctly signed images, not modified ones. Privilege acquired before flashing stock normally does **not** persist after replacing root-bearing boot chain; an independent post-boot loader/exploit must be demonstrated. FolkPatch startup scripts are not an independent KernelSU root migration.

Exact stock `boot.img`: gzip compressed kernel begins offset `4096`; decompressed ARM64 `Image` size `33,380,864`, SHA-256 `8edf4545acc10993e305271c2e05052d60093812d0f3374364d7cf3c8e6b52c7`. Actual stock kernel has `CONFIG_DEBUG_INFO_BTF=y`, `CONFIG_MODVERSIONS=y`, `CONFIG_KALLSYMS_ALL=y`, `CONFIG_KALLSYMS_BASE_RELATIVE=y`.

The extracted embedded BTF sits at ARM64 Image offset `23,857,508`, size `6,143,891`, SHA-256 `169aa6aac6c8ff3d78bbda9d1b0942da12c84c2f491fdcbb504c36260090f67e`. Parsed `141,882` BTF records: `61,049 FUNC`, `33,168 FUNC_PROTO`, `11,967 STRUCT`, `2,286 UNION`. Exact compiled structure anchors: `task_struct` size 4800 with `cred` offset 2080; `cred` size 184 with `security` offset 128; `file` 264; `f2fs_sb_info` 5992; `f2fs_inode_info` 1440; `f2fs_super_block` 3072; `f2fs_checkpoint` 192; `defex_context` 88. See repo doc:
https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/STOCK-HEZB1-6.6.89-EMBEDDED-BTF-ABI-EVIDENCE.md

Prior chat generated downloadable BTF + whole-kernel Ghidra script toolkit (`A146P_stock_6.6.89_BTF_and_decompilation_toolkit.zip`) and stock ARM64 `Image` in Library. **Function BODY C-like decompilation has NOT been completed**; BTF recovers types/prototypes/layout, not original source bodies.

## Source provenance / release
- Genuine Samsung GPL Android 15 user upload: `SM-A146P_15_Opensource.zip`, SHA-256 `7c7cd421d17f46138fe2a0c633882d96dcfa426b18593f4df52cbbd5823da197`, containing `Kernel.tar.gz` and `Platform.tar.gz`. Samsung `kernel-6.6/Makefile` = **6.6.50**, NOT device's shipping 6.6.89.
- Mirror user provided in GitHub release: https://github.com/wiredroid/Patch-Recovery/releases/tag/a146p-stock-source, asset `SM-A146P_15_Opensource.1.zip`.
- Google matching Android15 Linux 6.6.50 commit `4cdfe8c8c40affb63caa5e2626b52b0f8d47eca9`.
- Google official GKI 6.6.89 `android15-6.6-2025-06_r1` commit `ebbf6177d5ae521e9902af2816ef56ff366bccfa`, URL https://android.googlesource.com/kernel/common/+/refs/tags/android15-6.6-2025-06_r1.
- Reconstructed source = Samsung-specific delta from **matching 6.6.50 Google baseline** + official GKI89. It is a *hypothesis* about newer Samsung implementation, NOT verified exact Samsung A146PXXUHEZB1 GPL source.
- Stock `IKCONFIG` checked in at `a146p-stock/stock-A146PXXUHEZB1-6.6.89.config` (clang18, 4K pages, DEFEX, stock security, module versions).
- KernelSU Next pinned past commit `159bc7da4266fd9331f63e25901629db4b7bfff8`.
- Known-working **custom** Physwizz A146P kernel ref `6560c1ca1f009dd3e53b698245bf2df1b9804e03`; custom running kernel `6.6.89-android15-8-g6560c1ca1f00-dirty-physwizz`. User previously loaded experimental KernelSU Next `.ko` on this unlocked custom kernel (SHA-256 `5cc15a04c736982c4e5d7a025c67920dcd9aa45957503f0d90405f3b038acf07`). This is NOT stock proof. Do NOT fold Physwizz code into stock target.

## Verified CI milestones & downloadable artifacts
1. https://github.com/wiredroid/Patch-Recovery/actions/runs/38712679271 — Samsung GPL 6.6.50 versus matching Google 6.6.50: `81,653` identical common files, `219` shared modified, `225` Samsung-only, `328` Google-only. Vendor-change candidate set `444`.
2. https://github.com/wiredroid/Patch-Recovery/actions/runs/38710183690 — genuine Samsung-source 6.6.50 kernel and KernelSU Next `.ko` compilation passed. Output module `kernelsu-6.6.50-EXPERIMENTAL-NOT-FOR-LOADING.ko` SHA256 `ee66f2f07f46f7e9ebb6cab854d09274aa44137d9ee3b04d5bfa6ace1e08b473`; vermagic `6.6.50-4k SMP preempt mod_unload modversions aarch64`, `0` imported symbols absent from built System.map, `59` non-exported imports demanding special loader; not load-tested. Artifact https://github.com/wiredroid/Patch-Recovery/actions/runs/38710183690/artifacts/11960714480.
3. https://github.com/wiredroid/Patch-Recovery/actions/runs/38711730753 — same genuine Samsung 6.6.50 `.ko` plus `Image.gz` compiled. Neither is a safe drop-in for current stock `6.6.89`. Artifact https://github.com/wiredroid/Patch-Recovery/actions/runs/38711730753/artifacts/11961394304.
4. https://github.com/wiredroid/Patch-Recovery/actions/runs/38715878102 — partial Samsung 6.6.50 → Google 6.6.89 forward port success: `343` Samsung-modified paths cleanly retained, `44` genuine 3-way conflicts; all conflicted paths kept Google's GKI89 version instead of force-merging. This is PARTIAL (not exact stock), patch SHA256 `32eceb687814b50c00326822097b233f2b8e9520028bc76a91e7f30e956fd3b7`. Artifact https://github.com/wiredroid/Patch-Recovery/actions/runs/38715878102/artifacts/11962133064.
5. https://github.com/wiredroid/Patch-Recovery/actions/runs/38716664729 — pinned Physwizz A146P89 comparison on exactly 44 conflicts: `18` Physwizz files byte-identical to Google GKI89; `26` differ from both Google89 and Samsung50, needing semantic review. All 444 Samsung delta files vs Physwizz: `273` same as Samsung50, `96` distinct, `59` same as Google89, `16` all identical. Artifact https://github.com/wiredroid/Patch-Recovery/actions/runs/38716664729/artifacts/11963004146.
6. https://github.com/wiredroid/Patch-Recovery/actions/runs/38769981829 — Samsung MediaTek Galaxy A34 (MT6877) Linux6.6.89 reference audit successful. All 44 paths: `33` match GKI89, `2` match Physwizz A146P89, `9` differ. Of the original 26 distinct paths: `16` match GKI89, `2` Physwizz, `8` distinct. Artifact https://github.com/wiredroid/Patch-Recovery/actions/runs/38769981829/artifacts/11990912301. Reference tree https://github.com/Fede2782/kernel_samsung_mediatek_common pinned `6dfa2540bbfd95ed6475933f4b6f925c6a644e6c`.
7. https://github.com/wiredroid/Patch-Recovery/actions/runs/38771140866 — cross-variant audit success: MediaTek A145R 6.6.92 19 of 44 match Physwizz A146P89, 14 Google89, 11 distinct; Exynos A146B Linux5.15.197 has no exact matches on same 44 paths (36 distinct, 8 absent). Artifact https://github.com/wiredroid/Patch-Recovery/actions/runs/38771140866/artifacts/11990973786.
8. **LATEST stock-IKCONFIG vmlinux experiment FAILED** https://github.com/wiredroid/Patch-Recovery/actions/runs/38769715340, job `116542025665`, artifact https://github.com/wiredroid/Patch-Recovery/actions/runs/38769715340/artifacts/11990968946. First actual Clang compile failure (log line ~2387): `fs/f2fs/dir.c:1148:5: error: call to undeclared function 'print_block_data'`. Samsung `dir.c` references a helper not exposed by the retained newer GKI89 header. Earlier key mismatch: stock `CONFIG_SAMSUNG_GKI_KERNEL=y` was missing from candidate resolved config. Latest run tried ephemeral local dev signing key (NOT trusted Samsung signing); never claim this gives real locked-bootloader trust. Kernel fails before `vmlinux` or BTF compare. DO NOT claim a compiled stock kernel yet. Earlier failure diagnostics extraction run https://github.com/wiredroid/Patch-Recovery/actions/runs/38769179814 passed.

## More sibling-device/source research
- Public SM-A146U / SM-A146U1 US Android15 samples show `a14xm` and same MT6833; **no verified official A146U / U1 Android15 GPL kernel source ZIP found**. Android14 A146U real kernel sample `4.19.191`; do NOT assume Android15 A146U has 6.6.89. Research report:
  https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/A146U-US-KERNEL-SOURCE-SEARCH.md
- Samsung official source search https://opensource.samsung.com/uploadSearch?searchValue=A14 and Samsung request for source https://opensource.samsung.com/requestInquiry; user may need to authenticate and request `SM-A146U`, `SM-A146U1` or *EXACT `A146PXXUHEZB1` corresponding 6.6.89 GPL sources + config/build scripts, exported symbol list and Module.symvers*.
- Same a14xm `joeyduzit/a146p_a14xm_stock_kernel` is `6.6.50` not 6.6.89. `KKRTBUILDS/android_kernel_samsung_a14xm` and `RegonGaming/android_kernel_samsung_a14xm` are `4.19.191` older.
- A146B / A146M A14 5G are **Exynos 1330** and Android15 custom source Linux `5.15.197`; not direct MediaTek KMI/ABI analogs. Samsung official Exynos archive `SM-A146B_SWA_15_Opensource.zip` listed. A145R 4G Mediatek 6.6.92 and Galaxy A34 Mediatek 6.6.89 are better exact-era comparative references. No proven Snapdragon A14 5G SKU.
- Detailed comparison and variant docs:
  https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/CROSS-VARIANT-A14-A34-KERNEL-REFERENCES.md
  https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/A14-5G-variant-SoC-and-source-research.md
  https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/SIBLING-A146B-EXYNOS-SOURCE-PROVENANCE.md
  https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/Physwizz-6.6.89-44-conflict-semantic-triage.md

## How to continue engineering, in order
1. **FIRST:** fetch most recent GitHub branch HEAD, workflows, and the latest stock `vmlinux` build logs/artifact (newest currently `38769715340`). Fix `print_block_data` **semantically**: locate its true definition/prototype, config gates and callers in genuine Samsung A146P50 and A34 GKI89/A145R/Physwizz; port only minimally required compatible declarations/implementation into Google89 while preserving GKI89 F2FS changes. No dummy/stub, no `-Wno-error` or other failure masking. Commit on isolated branch; trigger CI; verify first ERROR moves/resolves.
2. Inspect candidate stock `olddefconfig` and original user stock config; investigate `CONFIG_SAMSUNG_GKI_KERNEL` missing, and any other important drift. Do not redefine a config blindly or fake stock key.
3. Incrementally resolve remaining **26 distinct source-level cases** (especially F2FS files/ondisk structs, `mm/vmscan.c`, `drivers/android/vendor_hooks.c`, tracepoints, DEFEX, device-mapper) with triangulation and tests. Do not copy entire Physwizz.
4. Once reconstructed source compiles `vmlinux` with matching stock config, extract its BTF and symbol table/`vmlinux.symvers`, compare **every relevant structure/member offset**, function prototypes, exported and non-exported kernel symbol presence, `CONFIG_MODVERSIONS` CRCs, Samsung-specific KMI, version magic, security behavior. User's real stock BTF is authoritative, Physwizz and sibling phones merely hints.
5. Only then build KernelSU Next stock-target `.ko`; label as *experimental untested* until a safe loader and device verification; no blind insmod into stock without matching ABI/module-signature policy.
6. Separately test (on unlocked BL and only after user permission, backup/rollback) migration from current Physwizz + FolkPatch to KernelSU boot-persistent root, without relying on FolkPatch for module insertion. Do not claim true independence from manual `insmod` or `service.d` run by FolkPatch.
7. Evaluate locked BL without touching OEM-signed images; stock compatible `.ko` alone is insufficient. Need documented *live*, model/firmware-specific runtime privilege and kernel module insertion capability with security systems. Proposed "GhostLock CVE-2026-43499" has **no verified A146P exploit or proof**, so never rely upon it.
8. The user's latest unresolved technical question: "Can we have root via FolkPatch, flash original stock `boot.img`/`init_boot.img`, attach `.ko`, and reboot?" Answer: prior root will not persist merely by flashing stock; running kernel and privileges change on reboot, init ramdisk loading is absent, signing/modversions/exports must match, and locked AVB is a separate constraint. No safe confirmed procedure currently. Explain this clearly before any flashing instructions.

## Automations already active — avoid duplicates
- Hourly condition-watch research task ID `6ad06be8ecf081918c44629d56240073`, title `A146P KernelSU build watch`, enabled, Australia/Sydney timezone, hourly cadence. Last observed run `2026-10-15T17:02:48Z`.
- One-shot morning report ID `6ad098bfd59881918a0f2b6f610ab7d4` scheduled `2026-10-16 08:00` Australia/Sydney flexible, enabled at last check.
- **Notifications_enabled=false and email_enabled=false** at last check, so user may not be alerted. Review current task state before changes.

## Important success/false-success distinctions
- A green workflow that produces a report or partial patch is NOT a boot-tested complete stock source.
- Stock BTF type recovery is NOT recovered original C function bodies. Ghidra script exists in original-chat toolkit but no completed whole-image decompilation was verified.
- Samsung official source Linux `6.6.50` differs from shipping `6.6.89`; module vermagic and CRC likely differ, can't load blindly.
- Any custom boot/init_boot modification changes SHA and is rejected by genuinely stock locked verified boot without trusted OEM signing.
- Maintain accurate evidence and links, no source contamination or cross-SoC ABI assertions, no dangerous flash instructions before compatibility and rollback are established.

## User's instruction to the next chat
"Continue this A146P Samsung-stock 6.6.89 / KernelSU Next work. Don't restart from scratch. Inspect the latest GitHub jobs; fix the real first compiler blocker and rebuild incrementally on the isolated branch. Keep simultaneous research on stock locked bootloader and safe FolkPatch-to-KernelSU handover. Clearly distinguish compilation, stock ABI matching, successful load, and locked bootloader root. Give concrete status and artifacts, not unsupported success claims."
