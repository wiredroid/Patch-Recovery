# US Galaxy A14 5G SM-A146U / SM-A146U1 kernel source investigation

Research date: 2026-10-16. **No verified A146U- or A146U1-specific Samsung GPL kernel source archive was found.** Do not invent an A146U download URL.

## Hardware relationship verified

- Public Android 15 SM-A146U user report: model `SM-A146U`, board/device `a14xm`, hardware `mt6833`, product `a14xmsq`: https://github.com/redphx/better-xcloud-devices/issues/21.
- Independent handset codename map groups `SM-A146P`, `SM-A146U`, `SM-A146U1`, `SM-A146W` under `a14xm`: https://github.com/KHwang9883/MobileModels/blob/master/brands/samsung_global_en.md. Device-report evidence for U is stronger than generic chipset comparison pages.
- One real SM-A146U Android 14 sample reported Linux kernel `4.19.191-27944104-abA146USQS6CXC2`: https://github.com/termux/termux-packages/issues/20039. Do not infer that the *Android 15* SM-A146U uses 4.19, or that it uses 6.6, without an actual boot image/version record.
- Samsung's official A146U Android 15 firmware history exists: https://doc.samsungmobile.com/SM-A146U/025664230214/eng.html. This is *firmware update history, not GPL source.*

## Authoritative source request

- Samsung Open Source Release Center: https://opensource.samsung.com/uploadSearch?searchValue=A14 (indexed view lists SM-A146P_15_Opensource.zip, A146B and others, but exact A146U filename/download is not verified).
- Samsung official **Request for source codes** form: https://opensource.samsung.com/requestInquiry. Select request for source codes and mobile/photography/PC. Request **SM-A146U and SM-A146U1 Android 15 complete corresponding Linux kernel source, build scripts/configs and vendor modules for specific A146USQU... / A146U1UEU... versions**. User authentication may be necessary; do not submit on behalf of user without permission.

## Verified public related sources, not A146U stock

- https://github.com/joeyduzit/a146p_a14xm_stock_kernel : Android 15 Samsung A146P MT6833 source mirror, `kernel-6.6/Makefile` verified to be **6.6.50**, NOT 6.6.89. Review against Samsung's user-provided official GPL archive before treating as independent.
- https://github.com/KKRTBUILDS/android_kernel_samsung_a14xm : same `a14xm` device family, `Makefile` verified **4.19.191**, older Android source and NOT 6.6.89.
- https://github.com/RegonGaming/android_kernel_samsung_a14xm : same `a14xm` family, `Makefile` verified **4.19.191**, not a direct match.
- https://github.com/forforksake/android_kernel_samsung_a146p : A146P Android 13 MT6833, substantially older version.
- Existing user's official Samsung Android 15 A146P `SM-A146P_15_Opensource.zip` source **6.6.50** remains strongest authoritative Samsung source.
- Existing exact user stock A146PXXUHEZB1 `boot.img` Linux **6.6.89** with extracted BTF remains the ABI target.

## Next evidence gates

1. If Samsung returns US A146U GPL release, verify archive SHA256 and `Makefile` version; do not assume `6.6.89`.
2. If official A146U archive includes Linux 6.6.89, compare against **matching Google Android15 6.6.89** and A146P 6.6.50 source, then correlate with exact A146P stock BTF and user IKCONFIG.
3. If A146U source is 4.19.191, restrict use to historical MT6833 device driver/security implementation references; avoid conflating ABI or using it to load modules on 6.6.89.
4. Never flash A146U boot.img/init_boot.img onto A146P. Carrier/DTB/vendor partitions, Samsung verified boot and model signatures may differ.
