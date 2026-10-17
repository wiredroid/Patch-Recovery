#!/usr/bin/env python3
"""Read-only research comparison: candidate .ko imported CRCs vs installed vendor module CRCs.

Mounted modules may be modified; matching release and CRCs do NOT authenticate
original Samsung HEZB1 firmware or prove module loading.
"""
import argparse
import csv
import json
from pathlib import Path
import re
import sys

EXPECTED = "6.6.89-android15-8-abA146PXXUHEZB1-4k"
HEX = re.compile(r"^0x[0-9a-fA-F]{1,8}$")


def normalize_crc(value):
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError(f"invalid CRC: {value!r}")
    return f"0x{int(value, 16):08x}"


def read_candidates(path):
    with path.open(newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        required = {"symbol", "status", "candidate_crc", "module_crc"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("candidate audit TSV missing required fields")
        rows = list(reader)
    if not rows or len({r["symbol"] for r in rows}) != len(rows):
        raise ValueError("empty or duplicate candidate imported symbols")
    return rows


def inspect(candidate, evidence):
    if evidence.get("expected_release") != EXPECTED:
        raise ValueError("reference vendor modules use a different kernel release")
    matched = evidence.get("matching_release_modules")
    if not isinstance(matched, list) or not matched:
        raise ValueError("no installed modules with exact original kernel release")
    symbols = evidence.get("symbols")
    conflicts = evidence.get("conflicting_symbols")
    if not isinstance(symbols, dict) or not isinstance(conflicts, dict):
        raise ValueError("invalid evidence: missing symbols / conflicts accounting")

    table = []
    for entry in candidate:
        name = entry["symbol"]
        reference = symbols.get(name)
        original = entry.get("module_crc", "")
        original = normalize_crc(original) if original else ""
        if reference is None:
            crcs = []
        else:
            if not isinstance(reference, dict) or not isinstance(reference.get("crcs"), list):
                raise ValueError("malformed CRC reference for " + name)
            crcs = sorted({normalize_crc(v) for v in reference["crcs"]})
            if not crcs:
                raise ValueError("empty reference for " + name)
        if len(crcs) > 1 or name in conflicts:
            result = "REFERENCE_CRC_CONFLICT"
        elif not crcs:
            result = "NO_EXACT_RELEASE_REFERENCE"
        elif not original:
            result = "REFERENCE_PRESENT_NO_RECONSTRUCTED_MODULE_CRC"
        elif crcs[0] == original:
            result = "MATCH_TO_INSTALLED_MODULE_REFERENCE_NOT_OEM_PROOF"
        else:
            result = "MISMATCH_TO_INSTALLED_MODULE_REFERENCE"
        table.append({
            "symbol": name,
            "reference_crc": ",".join(crcs),
            "candidate_ko_crc": original,
            "comparison": result,
            "candidate_import_status": entry["status"],
            "reference_module_names": ",".join(reference.get("module_names", [])) if reference else "",
        })

    counts = {s: sum(r["comparison"] == s for r in table)
              for s in sorted({r["comparison"] for r in table})}
    summary = {
        "target_release": EXPECTED,
        "reference_origin": "INSTALLED_VENDOR_MODULES_NOT_INDEPENDENTLY_AUTHENTICATED_AS_HEZB1_OEM",
        "device_modules_matched_release": len(matched),
        "device_crc_symbol_count": len(symbols),
        "candidate_import_count": len(table),
        "comparison_counts": counts,
        "oem_crc_verified": False,
        "ready_to_load": False,
        "factory_locked_root_demonstrated": False,
    }
    return summary, table


def audit(candidate_path, evidence_path, output_dir):
    candidate = read_candidates(candidate_path)
    evidence = json.loads(evidence_path.read_text())
    summary, rows = inspect(candidate, evidence)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "vendor-crc-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (output_dir / "vendor-crc-import-comparison.tsv").open("w", newline="") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    counts = summary["comparison_counts"]
    matches = counts.get("MATCH_TO_INSTALLED_MODULE_REFERENCE_NOT_OEM_PROOF", 0)
    conflicts = counts.get("REFERENCE_CRC_CONFLICT", 0)
    mismatches = counts.get("MISMATCH_TO_INSTALLED_MODULE_REFERENCE", 0)
    print(f"Candidates: {len(rows)}; installed-module CRC matches: {matches}; mismatches: {mismatches}; conflicts: {conflicts}")
    print("This is a read-only reference comparison; firmware origin and OEM module load compatibility are UNVERIFIED.")
    print("Reports:", output_dir)
    if conflicts or mismatches:
        raise ValueError("conflicting or mismatched CRC evidence; fail closed")
    if not matches:
        raise ValueError("no overlapping CRC evidence; fail closed")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-tsv", type=Path, required=True)
    p.add_argument("--reference-json", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    try:
        audit(a.candidate_tsv, a.reference_json, a.output)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as ex:
        sys.exit("FAIL CLOSED: " + str(ex))


if __name__ == "__main__":
    main()
