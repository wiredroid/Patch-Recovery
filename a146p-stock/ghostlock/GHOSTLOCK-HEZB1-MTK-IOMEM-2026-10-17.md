# OEM A146P GhostLock MediaTek physical-map follow-up — 2026-10-17

**Read-only research only. No live GhostLock run. Do not flash/relock.** Current installed running kernel: `6.6.89-android15-8-g6560c1ca1f00-dirty-physwizz`, not original Samsung signed OEM.

## Verified runtime `/proc/iomem` facts from same physical Galaxy A14 5G A146P

```text
40000000-4807ffff : System RAM
  40090000-41d2ffff : Kernel code
...
80000000-85ffffff : System RAM
```

- **Current runtime hardware RAM base is `0x40000000`**; this is a strong *candidate* for `kernel_phys_offset` on original OEM firmware because it reflects the physical SoC's DRAM layout, but it is not independently verified under an unmodified OEM kernel.
- `0x40090000` is the **Physwizz live `_stext` physical address**; DO NOT copy into the stock profile's `kernel_phys_load`.
- Stock OEM boot-image extractor reported `kernel_phys_load=0x80000000`. This is **not** independently measured from stock running code. Source [`tools/extract_rs/src/boot.rs`](https://github.com/YuKongA/ghostlock-app/blob/main/tools/extract_rs/src/boot.rs) hardcodes `MTK_VADDR_BASE=0xFFFFFFC000000000` and `MTK_DEFAULT_PHYS_LOAD=0x80000000`; [`main.rs`](https://github.com/YuKongA/ghostlock-app/blob/main/tools/extract_rs/src/main.rs) accepts this heuristic only when `_text - MTK_VADDR_BASE` equals that default. Do not call that a measured OEM DRAM base when the live map contradicts it.
- The [`iomem.rs`](https://github.com/YuKongA/ghostlock-app/blob/main/tools/extract_rs/src/iomem.rs) parser explicitly treats the smallest `System RAM` start as DRAM base. Its test case even contains this precise `0x40000000` RAM + `0x40090000` code layout. However, **do not mix the currently running Physwizz `/proc/iomem` with original OEM image to calculate an OEM `kernel_phys_load`**; that would combine two different kernels.

## Next independent stock loader evidence

[GhostLock vendor_boot.rs](https://github.com/YuKongA/ghostlock-app/blob/main/tools/extract_rs/src/vendor_boot.rs) reads only the 20-byte standard vendor_boot header:
`VNDRBOOT` magic at 0, header version u32 at 8, page size u32 at 12, physical `kernel_addr` u32 at 16.
A genuine unchanged HEZB1 `vendor_boot.img` (or header from running stock vendor_boot partition *if verified unmodified*) could provide independent physical load evidence. If `kernel_addr & 0xFFFFF == 0x80000`, upstream considers `kernel_phys_offset=kernel_addr-0x80000` justified for arm64 text alignment. If low 20 bits zero, vendor_boot alone yields load but not offset. All other low patterns are rejected by the upstream parser.

Suggested minimally invasive inspection, performed on current phone and output only, not file copying or flashing (requires rooted shell):
```sh
su -c 'p=/dev/block/by-name/vendor_boot; [ -b "$p" ] || p=/dev/block/bootdevice/by-name/vendor_boot; [ -b "$p" ] || { echo "vendor_boot partition not found" >&2; exit 1; }; echo "Reading first 20 bytes of $p" >&2; dd if="$p" bs=20 count=1 2>/dev/null' | od -An -tx1
```
Validate `VNDRBOOT` magic and compare decoded `kernel_addr` to original OEM's expected layout. Don't assume current vendor_boot original if modified via system update or other patching.

**Candidate remains UNVERIFIED and has `kernel_phys_offset=null`, `kernel_phys_load=0x80000000` extractor-derived pending independent confirmation. No exploit run.**
