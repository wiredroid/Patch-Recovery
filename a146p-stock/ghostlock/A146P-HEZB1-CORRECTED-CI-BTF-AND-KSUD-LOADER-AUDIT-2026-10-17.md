# A146P HEZB1 — corrected 6.6.89 GKI reconstruction vs OEM BTF; ksud loader audit
**2026-10-17; research-only; no stock locked bootloader or module load validated.**

## Corrected CI run

[CI run #38942607886](https://github.com/wiredroid/Patch-Recovery/actions/runs/38942607886) **completed success**, artifact [#12065247428](https://github.com/wiredroid/Patch-Recovery/actions/runs/38942607886/artifacts/12065247428).

- `VMLINUX_COMPILE_EXIT=0` of partial Samsung50 port + official Google GKI 6.6.89. Kernel SHA256 `vmlinux` can be found in artifact. **Not an OEM-reproduced vmlinux.**
- Experimental KernelSU Next v3.4.2 (pinned `159bc7da4266fd9331f63e25901629db4b7bfff8`) `EXPERIMENTAL_MODULE_COMPILE_EXIT=0`. Binaries explicitly NOT FOR LOADING on Samsung stock.
- Corrective Samsung BTF-confirmed `flush_group` patch succeeded. Exact stock BTF reference: `f2fs_mount_info` size 376, `flush_group` at byte 16; `f2fs_sb_info` size 5992, `gc_lock` at 2416. These two assertions pass, and all nine structural size checks now match.

## Independent, *member by member*, OEM-BTF comparison

Compared the genuine user-supplied OEM `stock_btf/btf_struct_members.tsv` from `A146P_stock_6.6.89_BTF_and_decompilation_toolkit.zip` to `pahole-structs/*.txt` extracted from the corrected CI artifact. It is crucial to distinguish positively parsed fields from unparsed anonymous / alignment declarations.

| Struct | OEM named fields | Exact matches | Offset mismatches | Cannot reliably parse |
|---|---:|---:|---:|---:|
| `task_struct` | 217 | 202 | **0** | 15 |
| `cred` | 25 | 25 | **0** | 0 |
| `file` | 21 | 21 | **0** | 0 |
| `f2fs_sb_info` | 196 | 196 | **0** | 0 |
| `f2fs_mount_info` | 28 | 28 | **0** | 0 |
| `f2fs_inode_info` | 50 | 50 | **0** | 0 |
| `f2fs_super_block` | 48 | 46 | **0** | 2 |
| `f2fs_checkpoint` | 22 | 21 | **0** | 1 |
| `defex_context` | 11 | 11 | **0** | 0 |
| **TOTAL** | **618** | **600** | **0** | **18** |

A matching offset of a field under nine structures is useful evidence of layout, **not** a substitute for OEM source, compiled function ABI or policy. Absent fields may be declarative artifacts; they were NOT counted as matches.

## KernelSU module and OEM ABI blockers confirmed independently from artifact bytes

- Corrected `.ko` SHA256 `3ed5fda0fd042af69f778876f223d3d803ae27042bcf3101d37d48cb5345ec0e`.
- Its `vermagic=6.6.89-4k-gebbf6177d5ae-dirty SMP preempt mod_unload modversions aarch64`, **NOT** the exact OEM `6.6.89-android15-8-abA146PXXUHEZB1-4k` release.
- 219 undefined ELF references; 160 exported by *partial reconstructed* `vmlinux.symvers` (16221 total exports); 59 not exported. Of those 59, 53 function names occur in genuine OEM BTF, and six are non-BTF-function names: `__tracepoint_sys_enter`, `init_mm`, `mntns_operations`, `selinux_blob_sizes`, `selinux_state`, `uts_sem`.
- `CONFIG_MODVERSIONS=y` and `CONFIG_MODULE_SIG_PROTECT=y` on original stock config. **Actual OEM export CRCs and key/policy enforcement remain unknown.** Research compiler used a development signing key and `KBUILD_MODPOST_WARN=1`; linker success does not prove `init_module` success.
- `f2fs_sb_info` formerly mismatched across 118 member offsets; now **all 196 are confirmed** after `0005` patch.

## Important upstream ksud late-load behavior (avoid overstating missing symbol blocker)

Pinned KernelSU Next [`userspace/ksuinit/src/lib.rs`](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/userspace/ksuinit/src/lib.rs) `load_module()` intentionally:
1. Parses `SHN_UNDEF` symbols from LKM ELF;
2. Attempts to resolve them by reading `/proc/kallsyms`, temporarily setting `/proc/sys/kernel/kptr_restrict` to 1 (requires sufficient privilege and LSM permission), converting matching symbols to absolute-address references in an in-memory copy;
3. Calls `init_module`; if kernel logs specifically show `vermagic` mismatch it may replace `.modinfo` and retry.
**Consequently, 59 modpost warnings are an explicit runtime-resolution prerequisite, not automatic proof every non-exported name is impossible.** Successful reading of addresses, correct relocation, matched OEM CRCs for exported references, module signature restrictions, Samsung DEFEX/RKP/KDP etc still need confirmation. A text-only vermagic replacement is NOT OEM ABI equivalence.

Pinned [`ksud late_load.rs`](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/userspace/ksud/src/late_load.rs) stages daemon then delegates to `ksuinit::load_module` for embedded `android15-6.6_kernelsu.ko`. A standalone `.ko` is not the full GhostLock loader integration: the correct `ksud` must embed exact compatible module and be discoverable from KernelSU Next manager.

## Separate integration CI

Workflow `.github/workflows/a146p-ghostlock-ksunext-integration-ci.yml` pins GhostLock upstream `847793ea7f936c241f38f2ca840d382162ac5256`, applies local Kotlin AndroidManifest package visibility / manager detection patch and runs Kotlin unit tests **without building an executable APK or executing GhostLock**.

**Hard stop**: Do not flash, relock, run GhostLock on KSU-patched Physwizz, install experimental `.ko` into OEM stock kernel or treat this ABI audit as a confirmed exploit.
