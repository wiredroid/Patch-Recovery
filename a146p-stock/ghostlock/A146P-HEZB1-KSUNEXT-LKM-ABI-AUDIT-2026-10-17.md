# A146P stock 6.6.89 + GhostLock + KernelSU Next: compiled module ABI audit — 2026-10-17

**STATUS: experimental LKM compiled; NOT stock-compatible, NOT loaded, NOT proven in GhostLock, NOT safe for locked bootloader or module insertion.** Phone stays unlocked and working with Physwizz+KernelSU Next.

## Exact provenance

- GitHub Actions completed run #38935550968: https://github.com/wiredroid/Patch-Recovery/actions/runs/38935550968
- CI artifact #12061943568: https://github.com/wiredroid/Patch-Recovery/actions/runs/38935550968/artifacts/12061943568
- Module path in artifact: research-module/BINARY-DO-NOT-LOAD/A146P-GKI89-PARTIAL-KSUNEXT-UNVERIFIED-DO-NOT-LOAD.ko (3,953,688 bytes). SHA256: 225b8238ea343d93e23c951104e2be8003dcd5c08870c1a2f5005918bd341e10
- Pinned KernelSU Next commit 159bc7da4266fd9331f63e25901629db4b7bfff8; version 33356/v3.4.2; source tree is a partial Samsung50-on-Google GKI89 with 44 unresolved Samsung source-port paths.
- Candidate vmlinux linked successfully and created 16,221-line vmlinux.symvers, which is NOT the Samsung OEM Module.symvers.
- Genuine OEM boot.img (SHA256 0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9) contains embedded BTF. We cross-checked against its btf_func_prototypes.tsv and btf_struct_members.tsv, NOT live Physwizz symbols.

## Module ELF imports and stock BTF

1. Module vermagic: 6.6.89-4k-gebbf6177d5ae-dirty SMP preempt mod_unload modversions aarch64.
2. Actual OEM release: 6.6.89-android15-8-abA146PXXUHEZB1-4k. Release mismatch is real; merely changing the vermagic text would NOT fix the ABI.
3. There are 219 unique undefined ELF imports from nm -u. Of these, 160 appear in the reconstructed Module.symvers (exported), and **59 are NOT exported** by that candidate kernel. Build returned exit 0 because KBUILD_MODPOST_WARN=1 allows unresolved warnings; the log lists 10 explicitly and suppresses the remaining 49.
4. Among 59 non-exported imports, **53 matching function names appear in real stock BTF as FUNC declarations**. This only supports existence of function type definitions; it does NOT establish kallsyms availability, actual export, dynamic resolution, binary compatibility, stable address, or a working loader.
5. The six remaining non-FUNC names are: __tracepoint_sys_enter, init_mm, mntns_operations, selinux_blob_sizes, selinux_state, uts_sem. The OEM BTF VAR coverage is incomplete for globals (mostly per-CPU), so this does NOT prove those variables are absent.
6. Genuine OEM export CRCs are unavailable. Stock IKCONFIG has CONFIG_MODVERSIONS=y, CONFIG_MODULE_SIG=y, CONFIG_MODULE_SIG_PROTECT=y, and an OEM MediaTek signing-key path. The CI research development signing key is NOT OEM-trusted.
7. Exact IKCONFIG audit: 4 compiler/toolchain version differences (Android Clang 18.0.0 vs Ubuntu Clang 18.1.3 etc.), and 1,546 options absent from the partial candidate; not all necessarily applicable but stock configuration remains not fully recreated.

## Original Samsung BTF vs candidate pahole named-member comparison

These are **direct, named and parseable byte offsets**, NOT recursive/transitive ABI proofs:

| Structure | OEM size | Candidate size | Common parsed fields | Offset matches | Mismatches |
|---|---:|---:|---:|---:|---:|
| task_struct | 4800 | 4800 | 202 | 202 | 0 |
| cred | 184 | 184 | 25 | 25 | 0 |
| file | 264 | 264 | 21 | 21 | 0 |
| f2fs_sb_info | 5992 | 5984 | 196 | 78 | **118** |
| f2fs_inode_info | 1440 | 1440 | 50 | 50 | 0 |
| f2fs_super_block | 3072 | 3072 | 46 | 46 | 0 |
| f2fs_checkpoint | 192 | 192 | 22 | 22 | 0 |
| defex_context | 88 | 88 | 11 | 11 | 0 |

**Root cause of 118 shifted fields:** genuine OEM BTF struct f2fs_mount_info is 376 bytes and contains kgid_t flush_group at byte offset 16. Original Google GKI89 lacks this Samsung-specific field, making candidate mount_info 368 bytes. Candidate f2fs_sb_info.mount_opt starts at 2040 as OEM, but candidate gc_lock is at 2408 vs OEM 2416; 118 subsequent common members shift by -8 bytes.

Corrective patch (previously present but unwired): a146p-stock/patches/0005-f2fs-restore-stock-confirmed-flush-group-layout.patch. It is now wired into CI workflow .github/workflows/a146p-stock-6.6.89-abi-build.yml at commit 86bf7e398e307d49887eab5cfd65244d91541339 and a hard post-build BTF gate checks mount_info=376, flush_group=16, sb_info=5992 and gc_lock=2416. New build run #38942607886 is in progress: https://github.com/wiredroid/Patch-Recovery/actions/runs/38942607886 . Do not claim success before results arrive.

## Reproducible module audit

Read-only fail-closed script: a146p-stock/tools/audit-ksunext-stock-abi.py
Run locally on a PC with the archived experimental ko and candidate symvers (not stock) and original OEM BTF TSV. Do NOT use this output as permission to load a module.

## Remaining stages

- Confirm new source patch passes CI compilation and exact OEM BTF gates.
- Obtain actual OEM stock export symbol CRCs and verify which of the 59 non-exported imports can be legally and reliably resolved, with attention to Samsung module protections and signing keys.
- Handle GhostLock Android manager integration: its prepareKsud() does not list KernelSU Next package com.rifsxd.ksunext; ksud late-load additionally requires embedding the correct LKM for android15-6.6 KMI.
- Original signed boot/init_boot must remain unchanged for stock+locked-bootloader research. No Odin flash, module insertion, or bootloader relock is part of this static audit.
- Samsung exact source inquiry has been submitted; daily official-source monitoring is active.
