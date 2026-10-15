# Galaxy A14 5G model variants and kernel-source relevance to stock A146PXXUHEZB1

Verified research as of 2026-10-16.

## Model / SoC

| Phone SKU | Chipset | Source usefulness |
|---|---|---|
| SM-A146P (our target) | MediaTek MT6833 Dimensity 700 | Exact hardware; official Samsung Android15 GPL source SM-A146P_15_Opensource.zip already downloaded. Kernel source 6.6.50; **shipping stock target is 6.6.89**. |
| SM-A146U / SM-A146U1 (US A14 5G) | Also MediaTek MT6833 Dimensity 700 | Better same-hardware reference than Exynos, but actual kernel generation must be verified for each firmware. Documented US A146U Android14 kernel 4.19.191; do not assume same Linux 6.6/KMI simply from shared SoC. |
| SM-A146B / SM-A146M | Exynos 1330 (s5e8535) | Check for Samsung-common security/DEFEX/F2FS/vendor-hook changes only; NOT a drop-in MediaTek kernel. |
| 'Snapdragon A14 5G' | NO verified Qualcomm Snapdragon SKU | Do not spend CI time on speculative model. A14 5G appears in MediaTek or Exynos versions; Snapdragon Galaxy A-series models are different products with different SoCs. |
| SM-A145xx Galaxy A14 4G | MediaTek Helio G80 or Exynos 850 | Different handset and kernel SoC; lower-priority. |

## Primary Samsung GPL source portal

https://opensource.samsung.com/uploadSearch?searchValue=A14

Listed Android15 source releases:
- **SM-A146B / SM-A146M Exynos 1330**: SM-A146B_SWA_15_Opensource.zip, build refs A146BXXU8DYF4 and A146MUBU8DYF4.
- **SM-A146P Dimensity 700**: SM-A146P_15_Opensource.zip, build A146PXXUBEYF5 (Samsung public portal). This exact original source is already acquired and SHA-256 verified in our build pipeline.
- Samsung additionally lists a shared **Android15 toolchain** for Galaxy A34 5G / Galaxy A14 5G MediaTek / Galaxy A05. See source portal.

## Independently verified community Exynos trees

- https://github.com/physwizz/a146b-a146m at main Makefile = Linux 5.15.197.
- https://github.com/devhunter1/android_kernel_samsung_s5e8535 at lineage-24.0 Makefile = Linux 5.15.211, TARGET_SOC=s5e8535.
- https://github.com/0xjavad/SM-A146B_AOSP_KERNEL at android13-u2 Makefile = Linux 5.15.78.
- https://github.com/gmh5225/A146B-KSU-2 at main Makefile = Linux 5.15.104; Android14 Exynos Kernelsu reference ONLY.

These are NOT 6.6.89 and should not be used to manufacture a misleading '6.6.89 stock kernel'. Exynos SOC-specific device trees, drivers, DTBs and export symbols are different from MediaTek.

## US A146U same-SoC evidence and caution

- https://phonedb.net/index.php?c=samsung_sm-a146u_galaxy_a14_5g_2023_standard_edition_td-lte_us__sm-s146vl__samsung_a146&id=21669&m=Device lists MT6833V/ZA.
- https://phonedb.net/index.php?c=samsung_sm-a146u1_galaxy_a14_5g_2023_standard_edition_td-lte_us__samsung_a146&id=21660&m=device lists MT6833V/ZA.
- https://github.com/redphx/better-xcloud-devices/issues/21 Android15 SM-A146U reports hardware mt6833; verification of chipset but not its kernel.
- https://github.com/termux/termux-packages/issues/20039 older SM-A146U's Android14 kernel reported Linux **4.19.191**, demonstrating why firmware kernel needs separate checking.
- https://samfw.com/firmware/SM-A146U/USC lists Android15 firmware A146USQUHEZC1 and later, but not kernel source. The actual boot image could be analyzed for BTF and Linux version if legally obtained from firmware; no pretense that it is A146P stock source.

## Recommended source reuse ranking

1. Exact user's original Samsung SM-A146P A146PXXUHEZB1 **stock Linux 6.6.89 boot kernel + BTF** (highest authority; already extracted).
2. Samsung SM-A146P Android15 official GPL Linux 6.6.50 and its vendor changes against MATCHING Google Android15 GKI 6.6.50; forward port to official GKI 6.6.89 (ongoing).
3. Other SM-A146P MediaTek A14 5G Android15 GPL revisions if published, and any A146U MediaTek reference AFTER checking kernel generation.
4. Exynos SM-A146B / SM-A146M Android15 GPL for common Samsung security/F2FS patches only.
5. Physwizz A146P 6.6.89 as reference-only known-working custom kernel, never proof of exact stock equivalence.
6. Qualcomm Snapdragon source for a different Samsung phone is low priority and cannot supply missing MediaTek-specific kernel code.

## Engineering constraints

No available public Exynos or US MediaTek source is established as the **exact** Samsung A146PXXUHEZB1 source revision. Our current vmlinux preflight run 38766492106 failed during source compile; inspect its report/compile-vmlinux.log artifact 11990246609 for actual first compiler error, rather than assuming an unrelated SoC source fixes it.

Preserve original Samsung-signed boot.img SHA256 0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9 and init_boot.img SHA256 a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976. Runtime privilege loading on stock locked verified-boot remains unproven.
