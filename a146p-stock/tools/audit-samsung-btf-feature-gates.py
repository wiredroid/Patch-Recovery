#!/usr/bin/env python3
"""Offline A146P Samsung RKP/DEFEX/KDP kernel prerequisite audit.

Reads a user-owned original Samsung stock BTF toolkit and stock IKCONFIG.
No kernel calls, loading, flashing, root activity or Play Integrity changes.
BTF declarations establish source prerequisites, NOT usable runtime hooks.
"""
import argparse
import csv
import io
import json
from pathlib import Path
import sys
import zipfile

FUNCTIONS = {
    "defex": ("get_task_creds", "set_task_creds", "task_defex_enforce"),
    "kdp": ("prepare_ro_creds", "kdp_assign_pgd", "kdp_usecount_dec_and_test"),
    "kdp_other": ("inc_rlimit_ucounts", "dec_rlimit_ucounts"),
    "rkp_kprobe_api": ("register_kprobe", "register_kretprobe"),
}
CONFIG = (
    "CONFIG_SECURITY_DEFEX", "CONFIG_KPROBES", "CONFIG_KRETPROBES",
    "CONFIG_MODULE_SIG_PROTECT", "CONFIG_MODVERSIONS",
    "CONFIG_SECURITY_SELINUX", "CONFIG_SAMSUNG_GKI_KERNEL",
)

def get_btf_prototypes(path):
    with zipfile.ZipFile(path) as archive:
        with archive.open("stock_btf/btf_func_prototypes.tsv") as raw:
            table = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8"), delimiter="\t")
            if not {"name", "type_id", "proto_id", "signature"}.issubset(table.fieldnames or []):
                raise ValueError("original BTF function declaration TSV has unexpected columns")
            signatures, count = {}, 0
            for record in table:
                signatures.setdefault(record["name"], set()).add(record["signature"])
                count += 1
            if count < 1000:
                raise ValueError("original Samsung BTF function declarations unexpectedly incomplete")
            return {name: sorted(values) for name, values in signatures.items()}, count

def get_config(path):
    opts = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("CONFIG_") and "=" in line:
            name, value = line.split("=", 1)
            opts[name] = value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            opts[line[2:-11]] = "n"
    return opts

def audit(btf, config):
    funcs, count = get_btf_prototypes(btf)
    opts = get_config(config)
    presences = {group: {name: funcs.get(name, []) for name in names} for group, names in FUNCTIONS.items()}
    all_found = {group: all(presences[group][name] for name in names) for group, names in FUNCTIONS.items()}
    rkp = all_found["rkp_kprobe_api"] and opts.get("CONFIG_KPROBES") == "y" and opts.get("CONFIG_KRETPROBES") == "y"
    defex = all_found["defex"] and opts.get("CONFIG_SECURITY_DEFEX") == "y"
    return {
        "device": "SM-A146P",
        "firmware": "A146PXXUHEZB1",
        "stock_release": "6.6.89-android15-8-abA146PXXUHEZB1-4k",
        "oem_btf_declared_function_count": count,
        "oem_function_signature_evidence": presences,
        "group_declarations_present": all_found,
        "stock_ikconfig": {name: opts.get(name, "NOT_DECLARED") for name in CONFIG},
        "experimental_research_build_flags": {
            "CONFIG_KSU_SAMSUNG_RKP": "y" if rkp else "n",
            "CONFIG_KSU_SAMSUNG_DEFEX": "y" if defex else "n",
            "CONFIG_KSU_SAMSUNG_KDP": "y" if all_found["kdp"] else "n",
            "CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT": "y",
        },
        "warnings": [
            "Offline BTF presence does not prove runtime symbol address or hook registration success.",
            "BTF absence is not proof that a function cannot exist in any binary form.",
            "This does not establish Samsung RKP behavior, Knox warranty bit or Play Strong Integrity.",
            "Never load the A146P research LKM on factory stock based on this result.",
        ],
        "module_safe_to_load": False,
        "google_play_strong_integrity_proven": False,
        "locked_stock_root_proven": False,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stock-btf-zip", type=Path, required=True)
    p.add_argument("--stock-config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        report = audit(args.stock_btf_zip, args.stock_config)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("Original BTF functions:", report["oem_btf_declared_function_count"])
        print("Required group declarations:", report["group_declarations_present"])
        print("Research flags:", report["experimental_research_build_flags"])
        print("NOT a stock module-load, Knox or Play Strong Integrity validation")
    except (OSError, ValueError, KeyError, UnicodeError, zipfile.BadZipFile) as err:
        sys.exit("OFFLINE EVIDENCE AUDIT FAILED: " + str(err))

if __name__ == "__main__":
    main()
