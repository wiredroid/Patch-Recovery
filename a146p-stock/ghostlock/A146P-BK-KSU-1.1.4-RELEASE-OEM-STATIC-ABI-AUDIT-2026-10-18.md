# BK-KSU v1.1.4 against original SM-A146P HEZB1 kernel — static compatibility assessment
**18 October 2026. Experimental research ONLY.**

## Release/source provenance
- Official [BK-KSU v1.1.4 release](https://github.com/bklynali/BK-KSU/releases/tag/v1.1.4), published 2026-10-17 at 15:01:15 UTC.
- Notes claim `Samsung RKP/KDP/DEFEX compatibility framework`, add a security/risk feature and advise **"Do not update if you are using GKI."** These are upstream *claims*, not tested A146P support.
- Inspected source tag `v1.1.4`. `userspace/ksud/src/late_load.rs` uses `android15-6.6_kernelsu.ko` RustEmbed asset and `ksuinit::load_module`. `userspace/ksuinit/src/lib.rs` relocates undefined ELF symbols via `/proc/kallsyms`, then calls `init_module`.
- `userspace/ksud/src/lkm_image.rs` includes useful **offline ARM64 Image KALLSYMS/BTF recovery** code; it is part of `boot-patch-v2`, which **writes a modified boot.img**. Reusing its metadata parser for offline A146P 59-symbol verification is plausible research, but boot-patching is incompatible with the factory-locked stock goal.
- `userspace/ksud/src/magica.rs` requires existing UID 0 before enabling ADB root; this is not a substitute for GhostLock's initial root primitive.
- BK-KSU `kernel/Kconfig` did not expose the explicitly named `CONFIG_KSU_SAMSUNG_RKP` / `CONFIG_KSU_SAMSUNG_DEFEX` switches used in our KernelSU Next reconstruction build. Verify release-note Samsung claims from actual code and device evidence, not title alone.

## Direct downloaded release binary static audit

| Metric | BK-KSU v1.1.4 public Android 15 6.6 .ko | Our pinned KernelSU Next experimental A146P module |
|---|---:|---:|
| SHA256 | `90ca2234cfe3a4ebdfb80519f7d93bae92bdf3c23d95f06bbf3a288323698b72` | `e84763f6f2dbed6616f2a98c4b6ec3a30e9a0b519ca15021ee3bf89eeea46e94` |
| ELF size | 466,480 bytes | 3,953,688 bytes |
| Kernel `vermagic` release | `6.6.127-4k-g46a034eca005-dirty` | OEM-labelled `6.6.89-android15-8-abA146PXXUHEZB1-4k` |
| ELF undefined imports | **254** | 219 |
| Import names exported by **original Samsung boot Image** | **190** | 160 |
| Imports absent from stock OEM built-in export table | **64** | 59 |
| Embedded `__versions` CRC records | **0** | 161 incl. `module_layout` |
| Import CRC agreement with genuine OEM | Not checkable (no embedded CRCs) | 160/160, separately recovered from OEM boot |

- **216 imported names shared** between BK-KSU and our pinned KSU Next research module; 38 BK-only imports; three KSU Next-only imports.
- Five of the BK-only imports are **also absent from genuine Samsung stock built-in export table**: `__set_fixmap`, `copy_to_kernel_nofault`, `dcache_clean_inval_poc`, `vma_interval_tree_iter_first`, `vma_interval_tree_iter_next`. The other 33 BK-only import names are present in the stock export table, but BK binary has no CRC records to validate.
- Important: BK-KSU's module still advertises `modversions` in `vermagic` yet ships with **zero `__versions` entries / no decoded extended CRCs**. This leaves stock `CONFIG_MODVERSIONS=y` load compatibility unverified and potentially blocked.
- Absence from built-in `__ksymtab` does not independently prove absence from all runtime module exports or inaccessible addresses; `kallsyms` relocation needs separate stock-runtime authorization.
- The release assets contain APK, ksud, and multiple KMI .ko artifacts. None were installed or executed; only the downloaded public .ko was parsed in the GitHub CI sandbox.

## Tests and reproducibility
- [Static BK-KSU vs research KernelSU Next CI #39049794291](https://github.com/wiredroid/Patch-Recovery/actions/runs/39049794291) **success**: downloaded BK asset with expected 466,480-byte release size; recorded hash, `modinfo`, 254 undefined imports and missing module CRCs; compared it against the pinned research CI `#38967262315`. The CI intentionally uploaded **reports only**, not runnable APKs or modules.
- Independently compared the 254 BK imports against all 16,238 exported names and CRCs extracted from the original Samsung HEZB1 stock `boot.img`, not the running Physwizz kernel. Result: 190 exported / 64 non-exported built-in OEM.
- A complete read-only evidence ZIP `A146P-BK-KSU-v1.1.4-OEM-static-compatibility-audit.zip` was generated locally with per-import classification. Does not include executable .ko.

## Assessment for factory-locked Samsung A146P
The prebuilt BK-KSU v1.1.4 .ko is **not a better A146P fit** than our pinned KernelSU Next build. Its Samsung compatibility release note may contain implementation techniques worth reviewing, and its offline `kallsyms` parser is potentially reusable for the 59-symbol investigation, but the public binary **does not** directly fix the ABI, module protections or stock-root exploit validation.

**DO NOT load BK-KSU .ko or update the installed manager on this evidence. Do not relock the bootloader or flash modified boot/init_boot.**
