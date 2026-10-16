#!/usr/bin/env python3
"""Read-only, fail-closed research audit for an experimental A146P KernelSU Next LKM.

--candidate-symvers describes a PARTIAL rebuilt kernel, NOT actual Samsung CRCs.
OEM BTF function types show declarations, NOT actual stable callable addresses.
This script never loads, inserts, signs, modifies or executes a kernel module.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        h = hashlib.sha256()
        for buf in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(buf)
        return h.hexdigest()


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE)


def audit(args):
    ko = Path(args.ko)
    symvers = Path(args.candidate_symvers)
    btf = Path(args.oem_btf_func_tsv)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    imports = sorted(set(
        line.split()[-1] for line in run("nm", "-u", str(ko)).splitlines()
        if line.split()
    ))
    if not imports:
        raise RuntimeError("Missing ELF undefined imports; unexpected module")
    modinfo = run("readelf", "-p", ".modinfo", str(ko))
    match = re.search(r"vermagic=([^\r\n]+)", modinfo)
    if not match:
        raise RuntimeError("Could not find module vermagic")
    vermagic = match.group(1).strip()

    exports = {}
    with symvers.open() as handle:
        for line in handle:
            cols = line.split()
            if len(cols) >= 4:
                exports[cols[1]] = {"crc": cols[0], "export": cols[3]}

    btf_functions = set()
    with btf.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row.get("name"):
                btf_functions.add(row["name"])

    rows = [{
        "symbol": symbol,
        "candidate_exported": int(symbol in exports),
        "oem_btf_function": int(symbol in btf_functions),
        "candidate_crc": exports.get(symbol, {}).get("crc", ""),
        "candidate_export_kind": exports.get(symbol, {}).get("export", ""),
    } for symbol in imports]
    with (out / "module-imports.tsv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    unexported = [r for r in rows if not r["candidate_exported"]]
    stock_btf_evidence = [r for r in unexported if r["oem_btf_function"]]
    others = [r for r in unexported if not r["oem_btf_function"]]
    observed_release = vermagic.split(" ", 1)[0]
    summary = {
        "module_sha256": sha256(ko),
        "candidate_symvers_sha256": sha256(symvers),
        "oem_btf_func_tsv_sha256": sha256(btf),
        "module_vermagic": vermagic,
        "expected_stock_uname_r": args.stock_release,
        "release_matches_stock": observed_release == args.stock_release,
        "total_undefined_imports": len(rows),
        "candidate_exported_imports": len(rows) - len(unexported),
        "candidate_nonexported_imports": len(unexported),
        "nonexported_with_oem_btf_function_type": len(stock_btf_evidence),
        "nonexported_without_oem_btf_function_type": len(others),
        "nonfunction_names": [r["symbol"] for r in others],
        "oem_crc_validation": "UNAVAILABLE: OEM Module.symvers not supplied",
        "stock_load_compatibility": "UNVERIFIED: do not insmod or late-load",
    }
    (out / "module-audit.json").write_text(json.dumps(summary, indent=2) + "\n")
    report = [
        "# A146P KernelSU Next LKM ABI audit (research-only)",
        "",
        "Experimental module SHA256: " + summary["module_sha256"],
        "Module vermagic: " + vermagic,
        "Genuine OEM kernel release: " + args.stock_release,
        "Exact vermagic release match: " + str(summary["release_matches_stock"]),
        "Undefined ELF references: " + str(len(rows)),
        "Exported by reconstructed candidate: " + str(len(rows) - len(unexported)),
        "Not exported by reconstruction: " + str(len(unexported)),
        "Those present in stock OEM BTF as FUNC: " + str(len(stock_btf_evidence)),
        "Non-FUNC symbols requiring independent OEM validation: " + str(len(others)),
        "",
        "Non-FUNC names: " + (", ".join(r["symbol"] for r in others) or "none"),
        "",
        "NO GO: original stock symbol CRCs, actual export policy, OEM signature trust,",
        "non-exported symbol resolution, complete ABI, and loader behavior remain unverified.",
        "An OEM BTF declaration does not prove that a function is exported, accessible",
        "at a stable address, callable, or binary-compatible with this module.",
        "",
        "Detailed classification in module-imports.tsv.",
        "",
    ]
    (out / "module-audit.md").write_text("\n".join(report))
    print(json.dumps(summary, indent=2))
    if args.strict and (not summary["release_matches_stock"] or unexported):
        raise SystemExit("FAIL-CLOSED: unverified stock ABI / release; do not load")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ko", required=True)
    ap.add_argument("--candidate-symvers", required=True)
    ap.add_argument("--oem-btf-func-tsv", required=True)
    ap.add_argument("--stock-release", default="6.6.89-android15-8-abA146PXXUHEZB1-4k")
    ap.add_argument("--output", required=True)
    ap.add_argument("--strict", action="store_true")
    audit(ap.parse_args())
