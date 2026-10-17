# A146P HEZB1: direct OEM `boot.img` export-symbol CRC extraction (2026-10-18)

**This study was run OFFLINE on the actual original Samsung image, NOT on the currently running Physwizz kernel. No root operations, stock exploit, firmware flash, `init_module` or kernel insertion was attempted.**

## Original image provenance

- Exact OEM `boot.img` SHA256: `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`.
- Exact OEM `init_boot.img` SHA256: `a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976`. This is a ramdisk-bearing v4 image and **contains no kernel**, so it cannot produce kernel exports or CRCs.
- Original boot's gzip ARM64 `Image` extracted to **33,380,864 bytes**, SHA256 `8edf4545acc10993e305271c2e05052d60093812d0f3374364d7cf3c8e6b52c7`, banner `Linux version 6.6.89-android15-8-abA146PXXUHEZB1-4k`.

## How CRC data was recovered (direct OEM data, not model guesses)

Mapped Samsung's compiled `__ksymtab` PREL32 name-offset entries to the corresponding u32 `__kcrctab` values using the same linker ordering, anchored on the identifiable `___ratelimit` export. Decoded **16,238 kernel export names and their exact binary CRCs**. Independently checked `__alloc_pages`, `module_layout`, `__check_object_size`, and all **160** research module symbol names with embedded CRC records. The symbol-index mapping is corroborated by the identical names and CRCs for **2,407 symbols** shared with the separately collected exact-HEZB1-release installed module reference, with **no mismatch**.

The candidate KernelSU Next `.ko` compared is the **experimental partial-GKI89 research module from successful [CI run #38967262315](https://github.com/wiredroid/Patch-Recovery/actions/runs/38967262315)**, NOT an original OEM-signed .ko.

## Direct original Samsung Image versus experimental KSU Next module

| Class | Count | Result |
|---|---:|---|
| Module imported symbols with a version CRC | **160** | **160/160 exact matches to original OEM kernel Image `__kcrctab`; zero mismatches** |
| Module imported symbols without version CRC | **59** | **Absent from the 16,238 decoded built-in OEM export-symbol table**, requiring independent runtime resolution/access checks |
| Separate `module_layout` record | **1** | Exact OEM CRC match `0x93b4d7ac` |
| All candidate ELF imports | **219** | 160 with directly proven OEM CRC equality; 59 non-exported by this OEM built-in table |

Examples of **formerly unknown** original Samsung CRCs now proven by direct binary extraction:

- `commit_creds`: `0x3fe1e894`
- `prepare_creds`: `0x9f420e42`
- `register_kprobe`: `0x0472cf3b`
- `unregister_kretprobe`: `0x5ff55291`
- `module_layout`: `0x93b4d7ac`

The **44 previously uncovered CRC references are now resolved against the original Samsung Image**. The previous mounted-vendor-module inventory provided a matching reference for 116 out of 160; direct stock Image extraction provided definitive symbol-aligned references for all 160.

The existing genuine OEM BTF contains FUNC declarations for 53 of the 59 non-exported imports; six names (`__tracepoint_sys_enter`, `init_mm`, `mntns_operations`, `selinux_blob_sizes`, `selinux_state`, `uts_sem`) are not BTF FUNC entries. BTF declarations **do not prove export status or callable live addresses**.

## Limitations and next investigation

This materially narrows the stock ABI question, but `CONFIG_MODVERSIONS` CRC equality is **not full kernel-function behavioral ABI validation**. Original kernel security policy, proprietary Samsung/MTK signing trust and protected-GKI namespaces, actual live `/proc/kallsyms` access, `ksuinit` symbol relocation, DEFEX/RKP/KDP, exploit success on factory-locked firmware, and persistence all remain **unverified**.

The 59 names absent from the decoded original built-in export table are the next technical focus. Other vendor modules or separate export namespaces may supply some names at runtime; absence from this table alone does not prove universal runtime absence. **Do not insert the experimental module into original stock firmware or relock the bootloader on this evidence.**

**Reproducible offline decoder, complete 16,238-name export/CRC map, all 219 per-import comparisons, and JSON summary are available in `A146P-ORIGINAL-SAMSUNG-BOOT-160-OF-160-CRC-AUDIT.zip` generated alongside this report; original personal boot/init_boot images are not uploaded to GitHub.**
