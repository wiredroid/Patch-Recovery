#!/usr/bin/env bash
# Samsung A146P / Physwizz 6.6.89 → KernelSU Next migration preflight.
# SAFE READ-ONLY ON PHONE: no dd, flashing, patching, rooting or deletion.
set -euo pipefail
command -v adb >/dev/null || { echo "ADB is required on the host" >&2; exit 1; }
if [[ "$(adb get-state 2>/dev/null)" != device ]]; then
  echo "Phone not authorized/connected to adb (enable USB debugging and approve prompt)" >&2
  exit 2
fi
printf '\n=== A146P KernelSU Next read-only migration preflight ===\n'
echo 'No writes or flashing are performed.'
echo
echo "== Kernel & Android =="
adb shell uname -r
adb shell getprop ro.build.version.release
adb shell getprop ro.build.fingerprint
echo
echo "== Bootloader & verified boot (do not relock) =="
adb shell getprop ro.boot.bootloader
adb shell getprop ro.boot.slot_suffix
adb shell getprop ro.boot.vbmeta.device_state
adb shell getprop ro.boot.verifiedbootstate
adb shell getprop ro.boot.flash.locked
echo
echo "== Boot image block names (read-only list) =="
adb shell "ls -l /dev/block/by-name/boot /dev/block/by-name/init_boot /dev/block/by-name/vendor_boot 2>&1 || true"
echo
echo "== Existing root (may trigger root manager permission prompt) =="
adb shell "su -c 'id'" || echo "No working root-grant response yet."
echo
echo "== Active boot and init_boot hashes from device (read-only) =="
adb shell "su -c 'sha256sum /dev/block/by-name/boot /dev/block/by-name/init_boot'" || echo "Could not hash both partitions: inspect block names/root."
echo
echo '== Manual confirmations required =='
echo '1. Is current kernel still Physwizz 6.6.89?'
echo '2. Do you have an exact clean/unpatched Physwizz boot.img for CURRENT kernel + firmware binary?'
echo '3. Do you have PC/Odin recovery and a FULL BACKUP of patched boot AND init_boot?'
echo '4. Is your old root manager FolkPatch/APatch rather than embedded KernelSU 0.9.5?'
echo '5. Is KernelSU-Next 3.4.2 manager installed?'
echo 'STOP HERE until the clean boot image, firmware revision, rollback plan and exact .ko have been independently verified.'
