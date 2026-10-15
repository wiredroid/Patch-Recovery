# Samsung Galaxy A14 5G sibling SoC sources (checked 2026-10-16)

## Confirmed split: exact model name is less important than matching kernel/SoC

- User's **SM-A146P**: MediaTek MT6833 / Dimensity 700, stock Android 15 firmware **A146PXXUHEZB1**, Linux `6.6.89-android15-8-abA146PXXUHEZB1-4k`. Actual OEM boot image, BTF, and config are our authoritative ABI reference. Existing Samsung GPL source `SM-A146P_15_Opensource.zip` is older Linux **6.6.50**, firmware A146PXXUBEYF5.
- Same Galaxy A14 **5G Exynos variant**: **SM-A146B / A146M**, Samsung Exynos 1330. Official Samsung GPL Android 15 source listing `SM-A146B_SWA_15_Opensource.zip`, firmware `A146BXXU8DYF4 / A146MUBU8DYF4`. Official portal https://opensource.samsung.com/uploadSearch?searchValue=A146B . This official ZIP has **NOT** been extracted or checked for precise 15 kernel version; do not assume it is Linux 6.6.89. A146B Android 15 date 2025-06-19 per https://doc.samsungmobile.com/SM-A146B/025563221227/ben-bd.html .
- Verified public Exynos source mirrors: https://github.com/0xjavad/SM-A146B_AOSP_KERNEL at `android13-u2` Makefile VERSION 5 PATCHLEVEL 15 SUBLEVEL 78, and https://github.com/HunterGaming1212/android_kernel_samsung_s5e8535 at its observed default ref Makefile VERSION 5 PATCHLEVEL 15 SUBLEVEL 167. These are NOT verified Android 15 official ZIP contents and NOT an ABI-matched 6.6.89 base.
- Same Galaxy A14 **4G** devices A145F include Exynos 850 and MediaTek Helio G80, and inspected https://github.com/donut6150/android_kernel_samsung_a14 uses Linux 5.10.238. Less relevant to MT6833 Android15 Linux6.6.89.
- **No verified Snapdragon Galaxy A14 5G variant or corresponding Snapdragon A146 source** found. Do not invent one; Galaxy A14 **5G** documented SM-A146B Exynos1330, SM-A146P MediaTek MT6833: https://www.gsmarena.com/samsung_galaxy_a14_5g-12004.php and https://en.wikipedia.org/wiki/Samsung_Galaxy_A14 .
- Particularly useful same-generation Samsung/MediaTek **different phone**: Galaxy A34 5G MediaTek 6.6.89 repo https://github.com/Fede2782/kernel_samsung_mediatek_common/tree/6dfa2540bbfd95ed6475933f4b6f925c6a644e6c . Verified official GKI89 comparisons from CI run https://github.com/wiredroid/Patch-Recovery/actions/runs/38769981829 show 33/44 A146P source conflicts match GKI89, 2 match Physwizz 6.6.89, 9 other. Still not A146P OEM stock.

## Interpretation / engineering guidance

Use A146B source *only* as a reference for shared Samsung DEFEX / product policy, SELinux integration, Galaxy A14 device family code organization, and possibly security and F2FS ideas; absolutely do not copy its Exynos SoC drivers, KMI, kernel .config, 5.15 F2FS layout, module CRCs, DTB/boot/init_boot images into A146P 6.6.89.

Concrete security difference in community Exynos source: `security/samsung/defex_lsm/Kconfig` has `depends on SECURITY && (!KCOV || SAMSUNG_PRODUCT_SHIP)` in the inspected 5.15.167 tree; exact Samsung stock 6.6.89 DEFEX gate and `CONFIG_SAMSUNG_GKI_KERNEL` differ and require verification against user's stock IKCONFIG / BTF, not assumptions.

For stock compatibility rank inputs:
1. Exact user A146P HEZB1 **boot Image+BTF+IKCONFIG** and source release for precisely A146PXXUHEZB1 (request Samsung GPL if not available).
2. Same A146P MT6833 actual Samsung 6.6.50 GPL vendor patchset, forward-ported on official Android15 6.6.89.
3. Samsung/MediaTek **6.6.89** A34 and pinned Physwizz **reference-only** for competing interpretations of changed common code.
4. Exynos1330 A14B/M Android15 official GPL for shared Samsung security-specific logic, NOT direct ABI or kernel source base.
5. No A14 5G Snapdragon branch without a verifiable actual model+source.

The original stock signed boot.img and init_boot.img must retain their OEM hashes for locked verified boot. A KernelSU .ko would require privileged runtime loading on genuinely locked firmware, which remains unverified. No sibling source eliminates that requirement.
