#!/usr/bin/env python3
"""Read-only integration contract audit for A146P GhostLock and KernelSU Next.

Checks pinned source contracts and a research .ko. Never executes GhostLock,
invokes ksud, inserts a module, builds an APK, changes a kernel or flashes.
Every produced status explicitly distinguishes source integration from OEM ABI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


STOCK_RELEASE = "6.6.89-android15-8-abA146PXXUHEZB1-4k"
EXPECTED_KMI = "android15-6.6"
KSU_MANAGER = "com.rifsxd.ksunext"
MODULE_ASSET = EXPECTED_KMI + "_kernelsu.ko"


def checked_read(path):
    if not path.is_file():
        raise ValueError("missing required source: " + str(path))
    return path.read_text(encoding="utf-8")


def hash_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def audit(args):
    ghostlock = Path(args.ghostlock_root)
    ksu = Path(args.ksunext_root)
    ko = Path(args.ko)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    script = checked_read(ghostlock / "src/core/attack/ops.cpp")
    repository = checked_read(ghostlock / "app/src/main/kotlin/com/ghostlock/app/data/AndroidGhostlockRepository.kt")
    manifest = checked_read(ghostlock / "app/src/main/AndroidManifest.xml")
    late_load = checked_read(ksu / "userspace/ksud/src/late_load.rs")
    cli = checked_read(ksu / "userspace/ksud/src/cli.rs")
    assets = checked_read(ksu / "userspace/ksud/src/assets.rs")
    ksuinit = checked_read(ksu / "userspace/ksuinit/src/lib.rs")

    requirements = {
        "ghostlock_kotlin_discovers_ksunext": KSU_MANAGER in repository and "libksud.so" in repository,
        "ghostlock_manifest_queries_ksunext": KSU_MANAGER in manifest,
        "ghostlock_native_invokes_kmi_late_load": bool(re.search(r"late-load --kmi .*--allow-shell", script)) and "$KMI" in script,
        "ghostlock_native_module_poll": "/proc/modules" in script and "kernelsu" in script,
        "ksunext_late_load_uses_kmi_asset": 'format!("{kmi}_kernelsu.ko")' in late_load and "assets::get_asset_data(&ko_name)" in late_load,
        "ksunext_default_manager_matches": 'String::from("com.rifsxd.ksunext")' in cli,
        "ksunext_aarch64_embeds_assets": 'folder = "bin/aarch64"' in assets and "RustEmbed" in assets,
        "ksunext_loader_handles_kallsyms": "/proc/kallsyms" in ksuinit and "init_module" in ksuinit,
        "ghostlock_native_ksunext_fallback": "com.rifsxd.ksunext*/lib/arm64/libksud.so" in script,
    }
    if not ko.is_file():
        raise ValueError("missing compiled research .ko: " + str(ko))
    digest = hash_file(ko)
    if digest != args.expected_sha256.lower():
        raise ValueError("research .ko hash mismatch: expected " + args.expected_sha256 + ", actual " + digest)

    readelf = subprocess.run(["readelf", "-p", ".modinfo", str(ko)], capture_output=True, text=True)
    if readelf.returncode:
        raise ValueError("cannot inspect module ELF .modinfo: " + readelf.stderr)
    m = re.search(r"vermagic=([^\r\n]+)", readelf.stdout)
    if not m:
        raise ValueError("module has no vermagic in .modinfo")
    vermagic = m.group(1).strip()
    source_release_matches = vermagic.split(" ", 1)[0] == STOCK_RELEASE
    requirements["module_has_usable_elf_modinfo"] = bool(vermagic)
    requirements["research_module_has_oem_vermagic"] = source_release_matches

    # The source-level contract can pass, but OEM stock ABI remains a hard gate.
    integration_fields = [k for k in requirements if k not in (
        "research_module_has_oem_vermagic"
    )]
    contract_ok = all(requirements[k] for k in integration_fields)
    outcome = {
        "purpose": "source-and-research-module-audit-only",
        "source_contract": "PASS" if contract_ok else "FAIL",
        "ready_to_load": False,
        "factory_locked_root_demonstrated": False,
        "genuine_oem_module_crc_match": "NOT VERIFIED",
        "genuine_oem_module_export_policy": "NOT VERIFIED",
        "genuine_oem_kernel_abi": "NOT VERIFIED",
        "ksud_binary_embeds_this_exact_module": "NOT VERIFIED",
        "ghostlock_success_on_oem_kernel": "NOT VERIFIED",
        "stock_release": STOCK_RELEASE,
        "expected_kmi": EXPECTED_KMI,
        "expected_ksud_asset": MODULE_ASSET,
        "experimental_ko_sha256": digest,
        "experimental_ko_vermagic": vermagic,
        "experimental_ko_vermagic_matches_stock": source_release_matches,
        "source_contract_checks": requirements,
    }
    (out / "handoff-audit.json").write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    summary = [
        "# GhostLock / KernelSU Next source-level handoff audit",
        "",
        "Source contract: **" + outcome["source_contract"] + "**",
        "Required embedded asset: `" + MODULE_ASSET + "`",
        "Research module SHA256: `" + digest + "`",
        "Research module vermagic: `" + vermagic + "`",
        "OEM release exact match: " + str(source_release_matches),
        "",
        "This audit **does not build, package or verify a matching ksud binary**.",
        "The installed manager may contain a generic embedded kernel module.",
        "Original OEM Module.symvers, load/export/security policy and working exploit are",
        "not independently proven. No .ko should be inserted or late-loaded on stock.",
        "",
        "## Source checks",
        "",
    ]
    summary += ["- " + k + ": " + ("PASS" if v else "FAIL") for k,v in requirements.items()]
    (out / "handoff-audit.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    if not contract_ok:
        raise RuntimeError("Pinned sources disagree on GhostLock -> ksud handoff")

    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ghostlock-root", required=True)
    p.add_argument("--ksunext-root", required=True)
    p.add_argument("--ko", required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--output", required=True)
    arguments = p.parse_args()
    try:
        audit(arguments)
    except (ValueError, RuntimeError) as ex:
        print("HANDOFF AUDIT FAILED: " + str(ex), file=sys.stderr)
        sys.exit(2)
