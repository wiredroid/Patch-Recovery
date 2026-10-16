#!/usr/bin/env python3
"""Read-only arm64 KernelSU .ko / PARTIAL reconstruction CRC checker.

The supplied vmlinux.symvers is never treated as Samsung's ORIGINAL OEM CRC map.
Non-exported references may require a separately verified runtime resolver.
No module loading, privilege escalation, signing or firmware modifications.
"""
import argparse
import csv
import json
from pathlib import Path
import struct
import subprocess
import sys


def capture(*cmd):
    return subprocess.check_output(cmd, text=True, stderr=subprocess.PIPE)


def section_bytes(path, name):
    listing = capture("readelf", "-SW", str(path))
    for line in listing.splitlines():
        fields = line.strip().split()
        if len(fields) > 6 and fields[1] == name:
            offset, size = int(fields[4], 16), int(fields[5], 16)
            data = path.read_bytes()
            if offset + size > len(data):
                raise ValueError("ELF section exceeds file length: " + name)
            return data[offset:offset + size]
    raise ValueError("Required ELF section not found: " + name)


def version_records(data):
    # arm64 Linux 6.6 struct modversion_info: u64 CRC + char name[56]
    if len(data) % 64:
        raise ValueError("Unexpected __versions entry width; refusing to guess")
    result = {}
    for offset in range(0, len(data), 64):
        crc = struct.unpack_from("<Q", data, offset)[0] & 0xffffffff
        name = data[offset + 8:offset + 64].split(b"\\0", 1)[0].decode("ascii")
        if not name or name in result:
            raise ValueError("Duplicate or empty __versions symbol: " + name)
        result[name] = crc
    return result


def read_symvers(path):
    exports = {}
    for number, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split()
        if not parts:
            continue
        if len(parts) < 4:
            raise ValueError(f"Malformed candidate symvers at line {number}")
        if parts[1] in exports:
            raise ValueError("Duplicate exported symbol " + parts[1])
        exports[parts[1]] = (int(parts[0], 16), parts[3])
    return exports


def audit(args):
    imports = sorted({line.split()[-1] for line in capture("nm", "-u", str(args.module)).splitlines() if line.strip()})
    if not imports:
        raise ValueError("No imported ELF symbols found")
    exports = read_symvers(args.candidate_symvers)
    versions = version_records(section_bytes(args.module, "__versions"))
    modinfo = section_bytes(args.module, ".modinfo").split(b"\\0")
    fields = [x[len(b"vermagic="):].decode("ascii") for x in modinfo if x.startswith(b"vermagic=")]
    if len(fields) != 1:
        raise ValueError("Missing or ambiguous module vermagic")
    vermagic = fields[0]
    actual_release = vermagic.split(" ", 1)[0]
    rows = []
    mismatches = []
    not_exported = []
    for name in imports:
        exported = name in exports
        mod_crc = versions.get(name)
        exp_crc, kind = exports[name] if exported else (None, "")
        if not exported:
            not_exported.append(name)
            status = "NOT_EXPORTED_BY_CANDIDATE_RUNTIME_CHECK_REQUIRED"
        elif mod_crc != exp_crc:
            mismatches.append(name)
            status = "CANDIDATE_CRC_MISMATCH"
        else:
            status = "CANDIDATE_CRC_MATCH_NOT_OEM_PROOF"
        rows.append({"symbol": name, "status": status, "candidate_crc": f"0x{exp_crc:08x}" if exp_crc is not None else "",
                     "module_crc": f"0x{mod_crc:08x}" if mod_crc is not None else "", "candidate_export_kind": kind})
    extras = sorted(set(versions) - set(imports) - {"module_layout"})
    summary = {
        "target_release": args.expected_release,
        "module_vermagic": vermagic,
        "release_string_matches_target": actual_release == args.expected_release,
        "import_count": len(imports),
        "reconstruction_exported_count": len(imports) - len(not_exported),
        "reconstruction_nonexported_count": len(not_exported),
        "reconstruction_export_crc_mismatches": mismatches,
        "module_version_record_count": len(versions),
        "module_layout_crc_record_present": "module_layout" in versions,
        "unexpected_version_record_names": extras,
        "nonexported_symbols": not_exported,
        "OEM_CRC_STATUS": "UNKNOWN_NO_ORIGINAL_SAMSUNG_MODULE_SYMVERS",
        "OEM_SIGNATURE_STATUS": "UNKNOWN_NO_STOCK_RUNTIME_TEST",
        "OEM_LOAD_STATUS": "NOT_TESTED_DO_NOT_LOAD",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "candidate-crc-audit.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (args.output / "candidate-import-audit.tsv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({k: v for k, v in summary.items() if k != "nonexported_symbols"}, indent=2))
    errors = []
    if mismatches:
        errors.append("candidate CRC mismatches found")
    if extras or "module_layout" not in versions:
        errors.append("unexpected or missing __versions record")
    if actual_release != args.expected_release:
        errors.append("module vermagic release mismatch (metadata only)")
    if errors:
        raise ValueError("; ".join(errors))
    print("RESEARCH CRC PASS: reconstructed kernel ONLY; OEM CRC, signing, security, GhostLock still unverified")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--candidate-symvers", type=Path, required=True)
    parser.add_argument("--expected-release", default="6.6.89-android15-8-abA146PXXUHEZB1-4k")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        audit(args)
    except (ValueError, OSError, subprocess.CalledProcessError) as err:
        print("FAIL: " + str(err), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
