#!/usr/bin/env python3
"""Read-only CRC evidence from OEM-release Samsung vendor_dlkm .ko files.

Inspects ELF64 AArch64 .ko files and accepts only exact HEZB1 vermagic release.
Does NOT invoke init_module or flash, modify, sign or execute kernel code.
Matching version strings do not independently authenticate a module's origin.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import struct
import sys

STOCK = "6.6.89-android15-8-abA146PXXUHEZB1-4k"
ROOTS = ("/vendor/lib/modules", "/vendor_dlkm/lib/modules",
         "/odm_dlkm/lib/modules", "/system_dlkm/lib/modules")


def elf_sections(path, required):
    with path.open("rb") as f:
        h = f.read(64)
        if len(h) != 64 or h[:4] != b"\x7fELF" or h[4:6] != b"\x02\x01":
            raise ValueError("not little-endian ELF64")
        if struct.unpack_from("<H", h, 18)[0] != 183:
            raise ValueError("not ARM64")
        pos = struct.unpack_from("<Q", h, 40)[0]
        entry_size, count, string_index = struct.unpack_from("<HHH", h, 58)
        size = path.stat().st_size
        if not count or count > 4096 or entry_size < 64 or string_index >= count:
            raise ValueError("unsupported ELF section table")
        if pos + count * entry_size > size:
            raise ValueError("bad section boundaries")
        f.seek(pos)
        table = f.read(count * entry_size)
        headers = []
        for i in range(count):
            entry = table[i * entry_size:(i+1)*entry_size]
            headers.append((struct.unpack_from("<I", entry, 0)[0],
                            struct.unpack_from("<Q", entry, 24)[0],
                            struct.unpack_from("<Q", entry, 32)[0]))
        so, ln = headers[string_index][1:]
        if so + ln > size or ln > 2_000_000:
            raise ValueError("invalid ELF string-table size")
        f.seek(so)
        strings = f.read(ln)
        data = {}
        for idx, offset, length in headers:
            if idx >= len(strings):
                continue
            end = strings.find(b"\x00", idx)
            if end == -1:
                continue
            name = strings[idx:end].decode("ascii", "replace")
            if name in required:
                if offset + length > size or length > 20_000_000:
                    raise ValueError("bad section size: " + name)
                f.seek(offset)
                data[name] = f.read(length)
        return data


def decode_mod(path):
    data = elf_sections(path, {".modinfo", "__versions",
                               "__version_ext_names", "__version_ext_crcs"})
    info = {}
    for item in data.get(".modinfo", b"").split(b"\x00"):
        if b"=" in item:
            key, value = item.split(b"=", 1)
            info.setdefault(key.decode("ascii"), value.decode("ascii", "replace"))
    release = info.get("vermagic", "").split(" ", 1)[0]
    crcs = {}
    raw = data.get("__versions", b"")
    if raw and len(raw) % 64:
        raise ValueError("non-64-byte __versions entries")
    for i in range(0, len(raw), 64):
        crc = struct.unpack_from("<Q", raw, i)[0] & 0xffffffff
        name = raw[i+8:i+64].split(b"\x00")[0].decode("ascii")
        if name:
            crcs[name] = crc
    if "__version_ext_names" in data and "__version_ext_crcs" in data:
        names = [name.decode("ascii") for name in data["__version_ext_names"].split(b"\x00") if name]
        raw = data["__version_ext_crcs"]
        if len(raw) != 4 * len(names):
            raise ValueError("invalid extended CRC table")
        for i, name in enumerate(names):
            value = struct.unpack_from("<I", raw, 4*i)[0]
            if name in crcs and crcs[name] != value:
                raise ValueError("conflicting CRC entries")
            crcs[name] = value
    return release, crcs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--release", default=STOCK)
    p.add_argument("--roots", nargs="*", default=ROOTS)
    p.add_argument("--output", default="/sdcard/Download/A146P-OEM-vendor-module-CRC-evidence.json")
    args = p.parse_args()
    paths = {}
    for root in args.roots:
        start = Path(root)
        if not start.exists():
            continue
        for ko in (start.rglob("*.ko") if start.is_dir() else [start]):
            try:
                paths.setdefault(str(ko.resolve()), ko)
            except OSError:
                continue
            if len(paths) >= 2000:
                break
    seen = defaultdict(list)
    same = []
    skipped = defaultdict(int)
    errors = []
    for ko in paths.values():
        try:
            release, crcs = decode_mod(ko)
            if release != args.release:
                skipped[release or "(no vermagic)"] += 1
                continue
            if not crcs:
                errors.append({"file": ko.name, "reason": "no module CRC records"})
                continue
            same.append({"file": ko.name, "symbol_count": len(crcs)})
            for sym, crc in crcs.items():
                seen[sym].append({"crc": f"0x{crc:08x}", "module": ko.name})
        except (ValueError, OSError, UnicodeError, struct.error) as ex:
            errors.append({"file": ko.name, "reason": str(ex)})
    conflicts = {s: rows for s, rows in seen.items() if len({r["crc"] for r in rows}) > 1}
    report = {
        "expected_release": args.release,
        "source_warning": "Installed modules may be modified; compare origin with exact genuine Samsung AP package before calling CRCs OEM",
        "status": "READ_ONLY_EVIDENCE_NOT_STOCK_KERNEL_LOAD_PROOF",
        "scanned": len(paths),
        "matching_release_modules": same,
        "nonmatching_release_counts": dict(skipped),
        "parse_errors": errors,
        "unique_symbol_count": len(seen),
        "conflicting_symbols": conflicts,
        "symbols": {s: {"crcs": sorted({r["crc"] for r in rows}),
                        "module_names": sorted({r["module"] for r in rows})}
                    for s, rows in sorted(seen.items())},
    }
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n")
    print("Scanned:", len(paths), " Matching stock-release modules:", len(same))
    print("CRC symbols:", len(seen), " Conflicts:", len(conflicts))
    print("Other kernel releases:", dict(skipped))
    print("Report:", dest)
    print("NOT A STOCK MODULE LOAD OR OEM SIGNING VALIDATION")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as ex:
        sys.exit("ERROR: " + str(ex))
