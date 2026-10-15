# A146P HEZB1 original IKCONFIG vs reconstructed GKI89 — audited drift

**Grounded diagnostic source:** [stock-source CI run 38778209850](https://github.com/wiredroid/Patch-Recovery/actions/runs/38778209850), [artifact 11994039755](https://github.com/wiredroid/Patch-Recovery/actions/runs/38778209850/artifacts/11994039755), files `original-stock-IKCONFIG.txt`, `resolved-GKI89-partial-stock-config.txt`, `CONFIG-drift-summary.txt`, `CONFIG-drift.tsv`, `CONFIG-missing-from-candidate.txt`. Isolated branch only.

Original genuine stock configuration: **7,886 explicit options** (including disabled CONFIG lines). Candidate source `olddefconfig` resolved **6,340 explicit options**. Exactly **1,546 stock options are absent in the candidate Kconfig**, while **four options present in both differ**; all four mismatches are build toolchain version values:

| Option | Exact stock | CI candidate |
| --- | --- | --- |
| `CONFIG_AS_VERSION` | `180000` | `180103` |
| `CONFIG_CLANG_VERSION` | `180000` | `180103` |
| `CONFIG_LLD_VERSION` | `180000` | `180103` |
| `CONFIG_CC_VERSION_TEXT` | Android Clang 18.0.0 `477610d4d0d9` | Ubuntu Clang 18.1.3 |

Of the missing stock options, prefix distribution includes **718 `MTK_*`**, **107 `DRM_*`**, **107 `DEVICE_*`**, **95 `COMMON_*`**, **57 `TOUCHSCREEN_*`**, **44 `SND_*`**, and **17 `TZDEV*`**. These are counts of absent Kconfig entries, **not** proof each option must be built into the GKI core: some functionality may be supplied by separate vendor modules/builds. Source and firmware partitions must be audited before classifying relevance.

Crucial missing stock options include **`CONFIG_TZDEV=m`**, **`CONFIG_SAMSUNG_GKI_KERNEL=y`**, and `CONFIG_SAMSUNG_PRODUCT_SHIP=y`. The actual original Samsung stock config also enables `CONFIG_F2FS_ML_BASED_STREAM_SEPARATION=y` and `CONFIG_F2FS_ML_STREAMID_FORCE_COLD=y`, both carried through `olddefconfig`. The candidate retains `CONFIG_MODVERSIONS=y`, `CONFIG_DEBUG_INFO_BTF=y`, `CONFIG_SECURITY_DEFEX=y`, and `CONFIG_MODULE_SIG_PROTECT=y`, but merely retaining config values does not prove the implementation or enforcement matches the shipping kernel.

**Security/build limitations:** The CI swaps the unavailable original OEM MediaTek module signing key for a throwaway research key, and the Clang toolchain is not exactly the OEM compiler. Even a fully linked candidate `vmlinux` is not the signed stock kernel. Exact stock symbol exports, BTF member types, symbol CRCs, vendor module-signature semantics, KDP/DEFEX/SELinux enforcement, and original boot image trust remain independent validation gates. **No `.ko` proven compatible with genuine stock.**

2026-10-16 conclusion: config drift is now numerically measured, **not solved**. Reject any blanket 'stock kernel built' or locked-bootloader root claims based on this preflight.
