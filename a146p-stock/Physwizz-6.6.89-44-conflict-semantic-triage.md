# Samsung A146P 6.6.50 → Google Android15 6.6.89: Physwizz reference triage

**Status: reference audit complete, source merge NOT complete; not safe to flash.**

- Verified GitHub Actions run: https://github.com/wiredroid/Patch-Recovery/actions/runs/38716664729
- Original partial port run: https://github.com/wiredroid/Patch-Recovery/actions/runs/38715878102
- Physwizz reference commit: `6560c1ca1f009dd3e53b698245bf2df1b9804e03`
- Official Android15 6.6.89 source commit: `ebbf6177d5ae521e9902af2816ef56ff366bccfa`
- Matching Android15 6.6.50 source commit: `4cdfe8c8c40affb63caa5e2626b52b0f8d47eca9`
- Samsung 6.6.50 GPL source archive: `SM-A146P_15_Opensource.1.zip`.
- Physical firmware target: Samsung A146PXXUHEZB1 kernel `6.6.89-android15-8-abA146PXXUHEZB1-4k`, **not** the Physwizz kernel.

## Verified results

44 of the original Samsung-to-GKI 6.6.89 three-way merges conflicted.
Exactly **18 of these 44** files are byte-for-byte the same in Physwizz 6.6.89 and official Google GKI 6.6.89.
The existing conservative partial port already retained GKI for these.
The **other 26** files differ from BOTH Google GKI 6.6.89 and Samsung GPL 6.6.50.
They require semantic porting, not blind replacement. No conflicting file matched Samsung GPL 6.6.50 exactly.

Across all 444 Samsung-modified or added files (including cleanly merged paths), Physwizz:
- retains the exact Samsung 6.6.50 version of **273**;
- is distinct from both Samsung 6.6.50 and Google 6.6.89 in **96**;
- matches Google 6.6.89 in **59**;
- matches all three in **16**.

These comparisons indicate some Samsung changes were retained in the working Physwizz 6.6.89 tree. They DO NOT establish the changes in Samsung's actual A146PXXUHEZB1 shipping 6.6.89 image.

## 26-file review backlog organized by subsystem

### F2FS filesystem and related on-disk metadata — 11 files (highest data-integrity priority)

- `fs/f2fs/compress.c`
- `fs/f2fs/data.c`
- `fs/f2fs/f2fs.h`
- `fs/f2fs/file.c`
- `fs/f2fs/gc.c`
- `fs/f2fs/node.c`
- `fs/f2fs/segment.c`
- `fs/f2fs/segment.h`
- `fs/f2fs/super.c`
- `fs/f2fs/sysfs.c`
- `include/linux/f2fs_fs.h`

Specific reference-only observations: Physwizz's `include/linux/f2fs_fs.h` has a changed reserved-field layout relative to Google GKI89. Physwizz's `fs/f2fs/sysfs.c`, `f2fs.h` and `gc.c` include substantial Samsung/Physwizz changes. Treat filesystem layout changes as potentially on-disk ABI-sensitive; do not merge or flash without structured review and tests.

### Core memory and Android trace integration — 4 files

- `mm/vmscan.c`
- `include/linux/gfp.h`
- `include/trace/hooks/mm.h`
- `drivers/android/vendor_hooks.c`

Physwizz exports additional memory-related tracepoints and changes allocation/reclaim hooks. Verify every new hook has matching declarations, export symbols, and required config gates. Keep GKI 6.6.89's upstream fixes.

### Device-mapper, USB, and device interfaces — 6 files

- `drivers/md/dm.c`
- `drivers/media/usb/uvc/uvc_driver.c`
- `drivers/usb/gadget/function/u_serial.c`
- `include/linux/hid.h`
- `include/ufs/ufshcd.h`
- `drivers/android/vendor_hooks.c` (cross-listed in memory/trace section)

Actual **unique** device/interface files are five; the vendor-hook file is listed here as a cross-reference. Check if changes are relevant to the MT6833-based A146P firmware before porting.

### Build and ABI inventory — 6 files

- `BUILD.bazel`
- `android/abi_gki_aarch64.stg`
- `android/abi_gki_aarch64_galaxy`
- `android/abi_gki_aarch64_honor`
- `android/abi_gki_aarch64_pixel`
- `android/abi_gki_aarch64_sunxi`

Do not copy foreign-device ABI lists into the A146P release baseline by default. Physwizz's `BUILD.bazel` disables strict KMI symbol-list mode (`kmi_symbol_list_strict_mode: False`); this is not a stock equivalence demonstration. Preserve the GKI 6.6.89 build baseline until a specific Samsung need is proven.

## Next validation gates

1. Derive focused three-way file-by-file diffs for the **26 distinct** paths; prioritize F2FS, tracepoints, memory allocation, and critical core files.
2. Produce a **separate, clearly labeled experimental** source-port candidate with all conflict decisions documented; keep Physwizz *reference only*.
3. Run Samsung stock IKCONFIG `olddefconfig` using `a146p-stock/stock-A146PXXUHEZB1-6.6.89.config`. Record unavailable stock Kconfig options.
4. Compile and audit exports, kernel symbol CRCs, and runtime assumptions without calling a successful build stock-compatible.
5. Only after validated boot-chain compatibility and actual on-device testing consider replacing root/boot assets. A locked Samsung bootloader will reject modified boot/init_boot without trusted signatures; a separate verified late privilege and module loader is required.

**Do not load a Samsung GPL 6.6.50 module on the running 6.6.89 kernel; do not flash an experimental source-derived Image.gz.**
