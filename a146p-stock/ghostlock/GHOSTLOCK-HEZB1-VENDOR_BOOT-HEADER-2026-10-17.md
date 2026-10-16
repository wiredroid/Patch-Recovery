# A146P HEZB1 GhostLock — live vendor_boot header resolves MediaTek phys mapping (2026-10-17)

**Status: image/header evidence only. UNVERIFIED exploit, UNVERIFIED stock module load, UNVERIFIED locked bootloader root.** No exploit launched or modified boot images.

## Original command and full user output

```text
su -c 'p=/dev/block/by-name/vendor_boot; [ -b "$p" ] || p=/dev/block/bootdevice/by-name/vendor_boot; [ -b "$p" ] || { echo "vendor_boot partition not found" >&2; exit 1; }; echo "Reading first 20 bytes of $p" >&2; dd if="$p" bs=20 count=1 2>/dev/null' | od -An -tx1
Reading first 20 bytes of /dev/block/by-name/vendor_boot
 56 4e 44 52 42 4f 4f 54 04 00 00 00 00 10 00 00
 00 00 08 40
```

Decode per upstream [`tools/extract_rs/src/vendor_boot.rs`](https://github.com/YuKongA/ghostlock-app/blob/main/tools/extract_rs/src/vendor_boot.rs):
- Offset 0-7: ASCII `VNDRBOOT`, genuine vendor_boot magic;
- 8-11: header version `4` little-endian;
- 12-15: page size `4096` (`0x1000`) little-endian;
- 16-19: kernel load `kernel_addr = 0x40080000` (`1074266112`) little-endian.
- Since `kernel_addr & 0xFFFFF == 0x80000`, official GhostLock ARM64 text-alignment classification derives `kernel_phys_offset = 0x40080000 - 0x80000 = 0x40000000` (`1073741824`).

This is consistent with the **same physical device's** current (modified Physwizz kernel) `/proc/iomem`:
```text
40000000-4807ffff : System RAM
  40090000-41d2ffff : Kernel code
...
80000000-85ffffff : System RAM
```
The 0x40090000 live code start is 0x10000 beyond vendor_boot kernel load address, a plausible arm64 start-of-text delta, *not* proof about OEM execution offsets.

## Competing static-image heuristic

Extracting from Samsung original `boot.img` alone returned `kernel_phys_load = 0x80000000`. The [source](https://github.com/YuKongA/ghostlock-app/blob/main/tools/extract_rs/src/main.rs) obtains this from `_text - MTK_VADDR_BASE` only if equal to hardcoded `MTK_DEFAULT_PHYS_LOAD=0x80000000`; that is not a measurement from vendor_boot or hardware DRAM. The actual Samsung vendor_boot v4 header is better physical-load evidence.

## New candidate

[`candidates/A146PXXUHEZB1-VENDORBOOT-ADDRESSES-UNVERIFIED.conf`](candidates/A146PXXUHEZB1-VENDORBOOT-ADDRESSES-UNVERIFIED.conf) changes only
```hocon
kernel_phys_load = 1074266112
kernel_phys_offset = 1073741824
```
and retains the 117,459 recovered OEM kallsyms, exact kernel release, select_stack derived shift -2, and 15/15 independently matched OEM BTF task offsets from previous candidate. Original pure boot-image candidate preserved separately.

## Limits / next static tests

- Live vendor_boot partition **has not been independently SHA256 verified against HEZB1 official firmware**. Running boot is Physwizz; init_boot is KernelSU Next modified; current bootloader unlocked; therefore inferences about original OEM bootloader-locked behavior are still unverified.
- The logged `nfnetlink_log_init x1 does not materialize nfulnl_logger` warning requires a separate code/symbol check. Preserve original extracted values rather than guessing.
- Do not launch GhostLock on patched Physwizz KSU: official developer MediaTek instructions say a KSU-patched kernel interferes with the exploit and physical-address tool.
- The stock 6.6.89 KSU Next module ABI/signature/loading stage is a separate unfinished engineering program. Even a successful root primitive would not by itself prove locked-bootloader persistent root.
