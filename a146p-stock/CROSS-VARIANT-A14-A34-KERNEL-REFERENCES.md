# A146P source reconstruction: Exynos A14 and MediaTek sister-device audit

**Research only: none of these images or kernel modules are interchangeable across phones.**

Target: genuine Samsung Galaxy A14 5G **SM-A146P**, MT6833 Dimensity 700, stock Android 15 **A146PXXUHEZB1**, Linux **6.6.89**. The original Samsung GPL A146P source published for Android 15 is Linux **6.6.50**.

## A14 family hardware

- A14 5G **SM-A146B/SM-A146M**, Exynos 1330: genuine family variant. Android15 custom kernel reference `physwizz/a146b-a146m` pinned SHA `ca3d9d1620926dc7cc6efa1511d9d86a16683afd` is **Linux 5.15.197**, NOT 6.6.89. Samsung's official Android 15 Exynos GPL source exists at https://opensource.samsung.com/uploadSearch?searchValue=A14 as `SM-A146B_SWA_15_Opensource.zip`; public custom repo is **not** a substitute for official original GPL source. Useful to understand Samsung security hooks and F2FS intent only.
- A14 **4G SM-A145R**, MediaTek MT6769 Helio G80: different phone, but `physwizz/A145r` Android15 kernel is Linux **6.6.92**, pinned SHA `652449d2c4e9e18ec41a3c4277ab8b2230534878`; closer in architecture and version. Official GPL archive `SM-A145R_EUR_15_Opensource.zip` listed on Samsung open-source site.
- No verified Snapdragon Galaxy A14 **5G** variant found. Do not assume one exists or look for stock Snapdragon kernel matching MT6833.
- Galaxy A34 **5G MediaTek MT6877**, a different model but Linux **6.6.89** source `Fede2782/kernel_samsung_mediatek_common` pinned SHA `6dfa2540bbfd95ed6475933f4b6f925c6a644e6c`; highly useful exact-version comparison of Samsung/MediaTek shared source.

## Verified 44-path comparisons

The original official Samsung50 to Google89 patch yielded 44 unresolved three-way merges. A separate previous run classified 18 of them as *already identical* between Physwizz A146P89 and Google89, leaving 26 distinct cases.

New **[cross-variant comparison run 38771140866](https://github.com/wiredroid/Patch-Recovery/actions/runs/38771140866)** checked 44 paths against pinned A145R and Exynos A146B:
- A145R MediaTek 6.6.92: 19 match byte-for-byte Physwizz A146P 6.6.89, 14 match official Google 6.6.89, 11 distinct.
- A146B Exynos 5.15.197: 36 differ from every compared A146P reference, 8 paths absent. No byte-for-byte exact match to Samsung A146P 6.6.50, Physwizz A146P 6.6.89, or Google GKI89 among these 44 paths.
- Full path-by-path report: https://github.com/wiredroid/Patch-Recovery/actions/runs/38771140866/artifacts/11990973786

**[MediaTek Galaxy A34 6.6.89 comparison run 38769981829](https://github.com/wiredroid/Patch-Recovery/actions/runs/38769981829)**:
- All 44 paths: 33 match official Google GKI89, 2 match Physwizz A146P89, 9 distinct.
- Among the 26 originally Physwizz-distinct paths: 16 match Google GKI89, 2 match Physwizz A146P89, 8 distinct.
- Full audit: https://github.com/wiredroid/Patch-Recovery/actions/runs/38769981829/artifacts/11990912301

## Practical implication

1. Prefer **actual stock A146PXXUHEZB1 BTF and compiled symbols** as the authoritative ABI target, not any other phone's source.
2. Triangulate **A34 GKI6.6.89**, **A145R GKI6.6.92**, **Physwizz A146P89**, and **Samsung A146P50** for **F2FS, memory management, vendor trace hooks, and DEFEX**; identify shared Samsung code and explain diverging source decisions. The fact that A34 matches GKI89 on most paths supports keeping new GKI89 code **as a working hypothesis**, not as proven A146P stock.
3. Because Exynos A146B is Linux5.15, use it for Samsung subsystem *concepts* rather than code-level 6.6.89 forward ports or symbol matching.
4. Do not port Snapdragon-specific drivers; no Snapdragon A14 5G 6.6.89 baseline identified.
5. Exact stock signed boot.img SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9` and init_boot.img `a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976` require byte-for-byte identical unchanged OEM images. They cannot be reproduced by modified KernelSU boot/init_boot.
6. Current isolated branch stock-config 6.6.89 research CI run `38769715340` still compiles; its output must be inspected before any module-ABI claims.

**Do not flash any cross-model source-built kernel or use a cross-model .ko on A146P.**
