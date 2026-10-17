#!/usr/bin/env python3
"""Read-only pinned BK-KSU versus KSU Next Samsung-hardening source gate.

A release-note claim of full Samsung support is not itself proof of factory-
locked A146P late-loading, ABI parity, or protection bypass. Never runs a
kernel module, modified boot image, privileged action, or exploit.
"""
import argparse
import json
from pathlib import Path
import sys


STOCK_RELEASE = "6.6.89-android15-8-abA146PXXUHEZB1-4k"
SAMSUNG_OPTIONS = (
    "KSU_SAMSUNG_KDP", "KSU_SAMSUNG_RKP",
    "KSU_SAMSUNG_DEFEX", "KSU_SAMSUNG_NO_PATCH_TEXT"
)
DEFEX_FUNCTIONS = ("get_task_creds", "set_task_creds", "task_defex_enforce")
KDP_FUNCTIONS = ("prepare_ro_creds", "kdp_assign_pgd", "kdp_usecount_dec_and_test")


def read_file(root, relative):
    p = root / relative
    if not p.is_file():
        raise ValueError("required source unavailable: " + str(p))
    return p.read_text(encoding="utf-8")


def report(args):
    bk, kn = Path(args.bk_root), Path(args.ksunext_root)
    stock = json.loads(Path(args.stock_btf_evidence).read_text())
    if stock.get("stock_kernel_release") != STOCK_RELEASE:
        raise ValueError("stock BTF evidence is not exact HEZB1 release")
    funcs = stock.get("target_function_presence", {})
    if any(not funcs.get(f, {}).get("present") for f in DEFEX_FUNCTIONS):
        raise ValueError("A146P DEFEX evidence unexpectedly absent")
    if any(funcs.get(f, {}).get("present") for f in KDP_FUNCTIONS):
        raise ValueError("KDP function evidence changed; reevaluate flags")

    bkc = read_file(bk, "kernel/Kconfig")
    knc = read_file(kn, "kernel/Kconfig")
    bkpatch = read_file(bk, "kernel/hook/arm64/patch_memory.c")
    knpatch = read_file(kn, "kernel/hook/arm64/patch_memory.c")
    bkarm = read_file(bk, "kernel/hook/arm64/syscall_hook.c")
    knarm = read_file(kn, "kernel/hook/arm64/syscall_hook.c")
    bklate = read_file(bk, "userspace/ksud/src/late_load.rs")
    knlate = read_file(kn, "userspace/ksud/src/late_load.rs")
    bkinit = read_file(bk, "userspace/ksuinit/src/lib.rs")
    kninit = read_file(kn, "userspace/ksuinit/src/lib.rs")
    knrkp = read_file(kn, "kernel/compat/samsung_rkp.c")
    knkdp = read_file(kn, "kernel/compat/samsung_kdp.c")
    kndefex = read_file(kn, "kernel/compat/samsung_defex.c")

    bkopts = {option: ("config " + option in bkc) for option in SAMSUNG_OPTIONS}
    knopts = {option: ("config " + option in knc) for option in SAMSUNG_OPTIONS}
    tests = {
        "bk_generic_arm64_fixmap_patch": "set_fixmap_offset" in bkpatch and "stop_machine(" in bkpatch,
        "bk_syscall_table_patch_code": "ksu_patch_text(&ksu_syscall_table" in bkarm,
        "bk_can_retrieve_embedded_lkm": 'format!("{kmi}_kernelsu.ko")' in bklate,
        "bk_late_load_uses_init_module": "ksuinit::load_module" in bklate and "init_module(&buffer" in bkinit,
        "bk_late_load_reads_kallsyms": '"/proc/kallsyms"' in bkinit,
        "bk_ksuinit_symbol_loader_identical_to_ksunext": bkinit == kninit,
        "ksunext_samsung_rkp_kprobes": "register_kprobe(" in knrkp and "register_kretprobe(" in knrkp,
        "ksunext_samsung_defex_helpers": all(f in kndefex for f in DEFEX_FUNCTIONS),
        "ksunext_samsung_kdp_helpers": all(f in knkdp for f in KDP_FUNCTIONS),
        "ksunext_samsung_no_patch_guard": "CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT" in knpatch and "EOPNOTSUPP" in knpatch,
        "ksunext_can_retrieve_embedded_lkm": 'format!("{kmi}_kernelsu.ko")' in knlate,
        "ksunext_late_load_uses_init_module": "ksuinit::load_module" in knlate and "init_module(&buffer" in kninit,
        "ksunext_generic_arm64_fixmap_impl_exists": "set_fixmap_offset" in knpatch,
        "ksunext_generic_syscall_table_patch_code_exists": "ksu_patch_text(&ksu_syscall_table" in knarm,
    }
    required_true = set(tests)
    required_true.difference_update({"ksunext_generic_syscall_table_patch_code_exists"}) # implementation may change
    if not all(tests[x] for x in required_true):
        raise ValueError("source comparison contract drift: " +
                         ", ".join(k for k in sorted(required_true) if not tests[k]))
    if not all(knopts.values()):
        raise ValueError("pinned KSU Next no longer provides all four Samsung Kconfig options")

    buildflags = {
        "KSU_SAMSUNG_RKP": True,
        "KSU_SAMSUNG_DEFEX": True,
        "KSU_SAMSUNG_NO_PATCH_TEXT": True,
        "KSU_SAMSUNG_KDP": False,
    }
    summary = {
        "audit_type": "pinned-source-offline-only",
        "bk_release": "v1.1.4",
        "bk_commit": "25c8d24ea06f0f8e19eda4d761e98d3e8c417131",
        "ksunext_commit": "159bc7da4266fd9331f63e25901629db4b7bfff8",
        "stock_release": STOCK_RELEASE,
        "bk_release_note_claim": "Samsung RKP/KDP/DEFEX compatibility framework",
        "bk_has_named_samsung_kconfig_options": bkopts,
        "ksunext_has_named_samsung_kconfig_options": knopts,
        "a146p_research_flags_already_selected": buildflags,
        "stock_btf_defex_func_present": list(DEFEX_FUNCTIONS),
        "stock_btf_kdp_func_not_declared": list(KDP_FUNCTIONS),
        "ksuinit_lib_rs_identical_blob_sha": "1a62d4c2b18197d338451a4c809edd1308acc481",
        "new_bk_ksuinit_loader_logic_to_cherry_pick": False,
        "source_checks": tests,
        "recommended_module_for_oem_loading": "NONE",
        "stock_oem_abi_verified_for_bk": False,
        "stock_runtime_security_policy_verified": False,
        "factory_locked_samsung_root_proven": False,
        "recommendation": (
            "Preserve the A146P KSU Next research branch and device. "
            "BK-KSU's claims are plausible at product level but the pinned v1.1.4 "
            "generic ARM64 source includes live syscall-table patching, "
            "and no dedicated Samsung KDP/DEFEX/RKP Kconfig choices appear "
            "in its kernel/Kconfig. Do not import unsafe live patch code or "
            "assume its generic LKM is OEM compatible."
        ),
    }
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "samsung-source-compatibility.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    md = [
        "# BK-KSU 1.1.4 Samsung framework versus A146P KSU Next",
        "",
        "This is a pinned-source audit, not a live security bypass or module insertion.",
        "",
        "| Source feature | BK-KSU v1.1.4 | KSU Next v3.4.2 |",
        "|---|---|---|",
    ]
    for op in SAMSUNG_OPTIONS:
        md.append("| `" + op + "` Kconfig | " +
                  ("present" if bkopts[op] else "not declared") + " | " +
                  ("present" if knopts[op] else "not declared") + " |")
    md += ["", "## Source-path facts", ""]
    md += ["- " + k + ": " + ("yes" if v else "no") for k,v in tests.items()]
    md += [
        "",
        "## A146P original Samsung boot.img BTF evidence",
        "",
        "- DEFEX helper declarations present: " + ", ".join(DEFEX_FUNCTIONS),
        "- KDP helper declarations absent: " + ", ".join(KDP_FUNCTIONS),
        "- Existing A146P candidate deliberately enables RKP and DEFEX,",
        "  disables KDP and live text/data patching.",
        "- BTF visibility alone cannot validate kprobe registration, kernel export",
        "  protections, actual runtime function addresses, or locked-root exploit.",
        "",
        "**Neither project is proven root-capable on factory-locked stock A146P.**",
    ]
    (output / "samsung-source-compatibility.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bk-root", required=True)
    ap.add_argument("--ksunext-root", required=True)
    ap.add_argument("--stock-btf-evidence", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    try:
        report(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        sys.exit("FAIL CLOSED: " + str(exc))
