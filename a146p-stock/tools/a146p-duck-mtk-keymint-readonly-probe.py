#!/usr/bin/env python3
"""Samsung SM-A146P MediaTek RKP/KeyMint service inventory for Duck ToolBox.

READ-ONLY. No trustlet commands, certificate requests, key generation,
KeyMint operations, shell code injection, system setting changes, or root
escalation. Prints metadata only; never collects identifiers, serial numbers,
build fingerprint strings, CSR/certificates, private keys, or attestation IDs.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

OUTPUT = "/sdcard/Download/A146P-Duck-MediaTek-KeyMint-capabilities.json"
PROPERTIES = (
    "ro.product.model", "ro.hardware", "ro.board.platform",
    "ro.soc.manufacturer", "ro.soc.model", "ro.vendor.soc.manufacturer",
    "ro.vendor.soc.model", "ro.build.version.release", "ro.build.version.sdk",
    "ro.build.version.security_patch", "ro.vendor.build.security_patch",
    "ro.boot.verifiedbootstate", "ro.boot.vbmeta.device_state",
    "ro.boot.flash.locked",
)
DRIVERS = (
    "/dev/smcinvoke", "/dev/tee0", "/dev/tee1",
    "/dev/teepriv0", "/dev/mobicore", "/dev/trusty-ipc-dev0",
    "/dev/teei_client", "/dev/teei0", "/dev/utdriver",
)
LOOK_IN = (
    "/vendor/lib64", "/vendor/lib64/hw", "/vendor/bin/hw",
    "/odm/lib64", "/odm/lib64/hw", "/odm/bin/hw",
    "/system/lib64/hw", "/system_ext/lib64/hw",
)
HAL_FILE = re.compile(
    r"(keymint|keymaster|remote.provision|rkpd|tee|trustonic|mobicore|"
    r"microtrust|mtee|smcinvoke|gatekeeper|secureclock|sharedsecret)",
    re.IGNORECASE,
)
SERVICE = re.compile(
    r"(keymint|keymaster|remotelyprovision|remote_provision|rkpd|"
    r"gatekeeper|secureclock|sharedsecret)",
    re.IGNORECASE,
)
TA_PATTERNS = re.compile(
    r"(keymint|keymaster|remote.provision|rkpd|trustonic|microtrust|"
    r"mtee|tee|gatekeeper)",
    re.IGNORECASE,
)
# Exclude any accidental hardware IDs (model and SoC labels are fine).
def safe_value(key, val):
    val = val.strip()[:95]
    if key in ("ro.product.model", "ro.hardware", "ro.board.platform",
               "ro.soc.manufacturer", "ro.soc.model",
               "ro.vendor.soc.manufacturer", "ro.vendor.soc.model"):
        if not re.fullmatch(r"[-a-zA-Z0-9_. +/]{0,95}", val):
            return "(omitted: unexpected characters)"
    return val

def run(command, timeout=12):
    try:
        p = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout,
            errors="replace", check=False
        )
        return p.stdout if p.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""

def available_paths(root, pattern, limit=100):
    base = Path(root)
    found = []
    try:
        if not base.is_dir():
            return found
        for p in base.iterdir():
            if pattern.search(p.name) and (p.is_file() or p.is_symlink()):
                found.append(str(p))
            if len(found) >= limit:
                break
    except OSError:
        pass
    return found

def collect():
    props = {k: safe_value(k, run(["/system/bin/getprop", k]))
             for k in PROPERTIES}
    all_services = run(["/system/bin/service", "list"], timeout=18)
    relevant_services = []
    for line in all_services.splitlines():
        if SERVICE.search(line):
            # The output should contain service interface types, no data payload.
            # Limit to the service name, discarding bracketed descriptors.
            m = re.match(r"\s*\d+\s+([^:]+):", line)
            if m:
                relevant_services.append(m.group(1).strip()[:180])
    nodes = {path: os.path.exists(path) for path in DRIVERS}
    candidate_files = []
    for root in LOOK_IN:
        candidate_files.extend(available_paths(root, HAL_FILE))
    candidate_files = sorted(set(candidate_files))[:180]
    # Only paths under these fixed public locations; no filesystem content read.
    rkp_app_paths = []
    for root in (
        "/apex/com.android.rkpd/priv-app",
        "/apex/com.android.rkpd/app",
        "/system/priv-app",
        "/system_ext/priv-app",
        "/product/priv-app",
    ):
        rkp_app_paths.extend(available_paths(root, TA_PATTERNS))
    rkp_app_paths = sorted(set(rkp_app_paths))
    qualcomm_abi = {
        "keymasterdeviceutils_so_present":
            os.path.isfile("/vendor/lib64/libkeymasterdeviceutils.so"),
        "smcinvoke_present": nodes["/dev/smcinvoke"],
    }
    vendor_label = " ".join(props.get(x, "") for x in (
        "ro.soc.manufacturer", "ro.vendor.soc.manufacturer",
        "ro.hardware", "ro.board.platform"
    )).lower()
    media_tek = any(term in vendor_label for term in (
        "mediatek", "mtk", "mt6833", "mt68", "mt67", "mt65"
    ))
    return {
        "tool": "A146P Duck ToolBox MediaTek RKP prerequisites, read only",
        "target": "SM-A146P original Samsung HEZB1 / running Physwizz",
        "note": "Shows presence of services, files and drivers only; it cannot establish whether KeyMint will sign a supplied public key.",
        "device_properties": props,
        "running_as_root": run(["/system/bin/id", "-u"]).strip() == "0",
        "relevant_android_service_names": sorted(set(relevant_services)),
        "keymint_vendor_files": candidate_files,
        "rkp_package_paths": rkp_app_paths,
        "tee_device_nodes": nodes,
        "duck_qualcomm_v2_prerequisites": qualcomm_abi,
        "mediatek_detected": media_tek,
        "duck_rkp_device_provision_implemented_for_mtk": False,
        "no_tee_commands_executed": True,
        "no_certificates_or_secrets_read": True,
        "no_device_state_changed": True,
    }

def main():
    data = collect()
    dest = Path(OUTPUT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("MediaTek detected:", data["mediatek_detected"])
    print("Relevant service names:", len(data["relevant_android_service_names"]))
    print("Candidate HAL libraries/files:", len(data["keymint_vendor_files"]))
    print("Qualcomm-only Duck v2 prerequisites:",
          data["duck_qualcomm_v2_prerequisites"])
    print("MTK Duck issuance support implemented: False (upstream)")
    print("Saved read-only report:", str(dest))
    print("Do not run Duck provision or share keys/certificates.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as err:
        sys.exit("READ-ONLY PROBE FAILED: " + str(err))
