# A146P HEZB1 — installed stock-release modules vs KernelSU Next LKM import CRCs
**17 October 2026 · Read-only ABI research, not OEM root or module-load validation**

## Evidence and provenance
- Owner extracted 251 on-device modules from their currently Physwizz-rooted SM-A146P with script `a146p-stock/tools/extract-installed-oem-module-crcs.py`. All 251 report `6.6.89-android15-8-abA146PXXUHEZB1-4k`; 3,858 unique CRC symbol names; **zero conflicts**, zero file/directory parse errors. `/odm_dlkm/lib/modules` is absent.
- Source file `A146P-OEM-vendor-module-CRC-evidence.json`, SHA256 `9f5cdf7624d08fa806eb229fba838e27bddff780a3d13b8217eed2f4b40a5f4c` (not committed; owner-uploaded file).
- Pinned successful reconstructed-kernel [CI run #38967262315](https://github.com/wiredroid/Patch-Recovery/actions/runs/38967262315) with artifact #12077210520: candidate .ko SHA256 `e84763f6f2dbed6616f2a98c4b6ec3a30e9a0b519ca15021ee3bf89eeea46e94`, source/research artifact ZIP SHA256 `a6930cb3eb734f8ba8898d62a619f9dbea5fdb0c2a0275a3185578d61962f3b8`.
- Verified the candidate .ko ELF64 ARM64 `__versions` section independently (161 CRC records including `module_layout`) and cross-checked imported-symbol CRCs against CI report `research-module/strict-crc-audit/candidate-import-audit.tsv`. No research .ko was executed, loaded or copied to device.

## Verified comparison results

| Imported symbol category | Exact installed-module CRC match | No installed-module CRC reference | Mismatches |
|---|---:|---:|---:|
| 160 reconstructed-kernel-exported `.ko` imports | **116** | **44** | **0** |
| 59 reconstructed-nonexported `.ko` imports | 0 | **59** | 0 |
| `module_layout` (additional module version record) | **1** | 0 | **0** |
| **Total** | **117** | **103** | **0** |

- **72.5% (116/160)** of imported exported-symbol CRCs match an installed exact HEZB1-release reference. Zero mismatches among compared values, 44 unknown in this category.
- The extra important `module_layout` CRC is **`0x93b4d7ac`** in both the candidate experimental LKM and in all 251 reference modules.
- The 59 reconstruction-nonexported imports have no `__versions` CRC records in this LKM and cannot be validated with the exported-symbol CRC method. They still require independent availability/loader/privilege checks; a BTF function declaration is not export or callable proof.
- Representative matching imports: `___ratelimit`, `__alloc_pages`, `__arch_copy_from_user`, `__arch_copy_to_user`, `__check_object_size`. Representative remaining *exported* symbols with no reference include `commit_creds`, `prepare_creds`, `register_kprobe`, `unregister_kprobe`, `override_creds`, `filp_open`.

## Implications and next evidence

**This substantially strengthens ABI consistency evidence and rules out CRC mismatches for the 116 overlapping exported symbols and module_layout in the inspected mounted-module reference.** It is **not** a proof that the candidate research `.ko` is compatible with the original Samsung `vmlinux` in all respects, nor permission to attempt insertion.

1. The installed module files are on the currently Physwizz-rooted installation; exact `vermagic` and consistency across files alone do not cryptographically prove unchanged original Samsung `vendor_dlkm`/system_dlkm bytes. Compare binaries/hash against genuine firmware package partitions if available.
2. **44 exported references are absent from this vendor module inventory**, not proven mismatched. Full genuine OEM `Module.symvers` would cover them.
3. **59 other imports are not exported by the reconstructed kernel**, and require separate runtime symbol accessibility and behavior validation; Samsung `MODULE_SIG_PROTECT`, `DEFEX`, namespace, CRC, KDP/RKP and `ksud` privileges remain possible blockers.
4. Native GhostLock primitive success on original locked-stock kernel, actual module insertion, Android manager packaging, and persistence remain unverified.

Automated reference comparator `a146p-stock/tools/compare-oem-vendor-module-crcs.py` and its [CI unit/synthetic test #39014558152](https://github.com/wiredroid/Patch-Recovery/actions/runs/39014558152) were built before receipt of the owner's real reference data. The real comparison in this note was independently performed against the uploaded JSON and pinned actual CI ELF/TSV.

**Status: promising stock ABI evidence; not ready-to-load, not a demonstrated locked-bootloader root.**
