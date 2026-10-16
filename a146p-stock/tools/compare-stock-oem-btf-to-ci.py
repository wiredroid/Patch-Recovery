#!/usr/bin/env python3
"""Read-only OEM BTF vs reconstructed A146P GKI89 CI artifact comparison.

Inputs:
  --oem-zip   Original stock_btf toolkit ZIP from exact HEZB1 boot.img
  --ci-zip    GitHub Actions run ZIP containing pahole-structs/*.txt
  --out       Output directory for TSV reports

Does not establish stock ABI, kernel export CRCs, module policy, a working
exploit, or loader viability. Never loads or modifies a kernel module.
"""
import argparse
import collections
import csv
import io
import json
import re
import zipfile
from pathlib import Path

STRUCTS = (
    "task_struct", "cred", "file", "f2fs_sb_info", "f2fs_mount_info",
    "f2fs_inode_info", "f2fs_super_block", "f2fs_checkpoint", "defex_context",
)
MIN_PARSED = {
    "task_struct": 202, "cred": 25, "file": 21, "f2fs_sb_info": 196,
    "f2fs_mount_info": 28, "f2fs_inode_info": 50,
    "f2fs_super_block": 46, "f2fs_checkpoint": 21, "defex_context": 11,
}

def get_text(z, path):
    return z.read(path).decode("utf-8")

def get_oem(z):
    grouped = collections.defaultdict(list)
    source = io.StringIO(get_text(z, "stock_btf/btf_struct_members.tsv"))
    for row in csv.DictReader(source, delimiter="\t"):
        if row["struct_or_union"] != "STRUCT" or row["name"] not in STRUCTS:
            continue
        if not row["member"]:
            continue  # An anonymous union isn't an independently named field.
        grouped[(row["name"], row["type_id"])].append(
            (row["member"], int(row["byte_offset"]))
        )
    result = {}
    for name in STRUCTS:
        choices = [(key, values) for key, values in grouped.items() if key[0] == name]
        if not choices:
            raise ValueError(f"Original OEM BTF missing {name}")
        variants = {frozenset(values) for _, values in choices}
        if len(variants) != 1:
            raise ValueError(f"Original OEM BTF duplicate struct variants disagree: {name}")
        result[name] = choices[0][1]
    return result

def get_candidate(z, name, known_names):
    text = get_text(z, f"pahole-structs/{name}.txt")
    offsets = collections.defaultdict(set)
    field_line = re.compile(r"^\s*(?!/).+?;\s*/\*\s*(\d+)\s+(\d+)\s*\*/")
    for line in text.splitlines():
        match = field_line.match(line)
        if not match:
            continue
        before = line.split(";", 1)[0]
        offset = int(match.group(1))
        matches = []
        for field in known_names:
            suffix = (
                r"\b" + re.escape(field) +
                r"\b\s*(?:\[[^\]]+\]\s*)*(?::\s*\d+\s*)?"
                r"(?:__attribute__\s*\(.*\)\s*)?$"
            )
            if re.search(suffix, before):
                matches.append(field)
        if len(matches) == 1:
            offsets[matches[0]].add(offset)
    sizes = re.findall(r"/\*\s*size:\s*(\d+)", text)
    return offsets, (int(sizes[-1]) if sizes else None)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--oem-zip", required=True)
    ap.add_argument("--ci-zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    with zipfile.ZipFile(args.oem_zip) as oem, zipfile.ZipFile(args.ci_zip) as ci:
        reference = get_oem(oem)
        rows, counts = [], []
        for name in STRUCTS:
            original = reference[name]
            offsets, size = get_candidate(ci, name, {member for member, _ in original})
            hits = misses = unparsed = 0
            for field, expected in original:
                actual = offsets.get(field, set())
                status = "MATCH" if expected in actual else (
                    "MISMATCH" if actual else "NOT_PARSED"
                )
                hits += status == "MATCH"
                misses += status == "MISMATCH"
                unparsed += status == "NOT_PARSED"
                rows.append({
                    "struct": name, "field": field, "stock_offset": expected,
                    "candidate_offsets": ",".join(map(str, sorted(actual))),
                    "status": status,
                })
            counts.append({
                "struct": name, "btf_named_fields": len(original),
                "matches": hits, "mismatches": misses, "not_parsed": unparsed,
                "candidate_size": size,
            })
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for filename, records in [("member-offsets.tsv", rows), ("structure-summary.tsv", counts)]:
        with (out / filename).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]), delimiter="\t")
            writer.writeheader()
            writer.writerows(records)
    print(json.dumps(counts, indent=2))
    if args.strict:
        for row in counts:
            if row["mismatches"] or row["matches"] < MIN_PARSED[row["struct"]]:
                raise SystemExit("FAIL CLOSED: insufficient matching OEM BTF evidence: " +
                                 row["struct"])
        print("PASS: parsed OEM BTF layout anchors; stock module compatibility remains UNVERIFIED.")

if __name__ == "__main__":
    main()
