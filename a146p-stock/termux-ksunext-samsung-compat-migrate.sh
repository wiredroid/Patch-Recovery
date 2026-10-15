#!/data/data/com.termux/files/usr/bin/bash
# SM-A146P Physwizz 6.6.89 -> KernelSU Next Samsung RKP/DEFEX candidate.
# Requires Termux + working FolkPatch root. Never runs unattended.
set -Eeuo pipefail
umask 077
WORK="$HOME/a146p-migration"
STAGE="/sdcard/Download/a146p-migration"
MOD_URL="https://github.com/wiredroid/Patch-Recovery/releases/download/a146p-ksunext-physwizz-6.6.89-samsung-exp2/kernelsu-a146p-physwizz-6.6.89-SAMSUNG-COMPAT-UNTESTED.ko"
MOD_SHA="1b92e9b7c3eb9e61c05b4ceae23a4fa980f1caeab81303a89b7ccfc032960f22"
INIT_SHA="a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976"
PHASE="preflight"
die() { printf '\nSTOP: %s\n' "$*" >&2; exit 1; }
on_error() { local rc="$?"; printf '\nFAILED in %s (exit %s). If boot writes already started, do NOT reboot until both partitions have been restored or verified.\n' "$PHASE" "$rc" >&2; exit "$rc"; }
trap on_error ERR
printf '\nA146P KernelSU Next v3.4.2: Samsung RKP/DEFEX Physwizz LKM candidate\n'
printf 'This is an UNTESTED boot/ABI combination. --flash requires typed confirmation.\n\n'
[ "${1:-}" = "--flash" ] || die "Usage: bash script.sh --flash (requires typed confirmation)"
[ "$(getprop ro.product.model)" = "SM-A146P" ] || die "Reported model is not SM-A146P."
case "$(uname -r)" in 6.6.89*physwizz*) ;; *) die "Running kernel is not expected Physwizz 6.6.89.";; esac
[ "$(getprop ro.build.version.release)" = "15" ] || die "Android version is not 15."
[ -d "$WORK" ] || die "Missing $WORK"
cd "$WORK"
for f in physwizz-folkpatch-boot.img init_boot-current-backup.img original-init_boot.img clean-physwizz-candidate.img kernel kptools ksud; do [ -s "$f" ] || die "Missing or empty $f"; done
for c in curl cmp sha256sum awk grep stat head dd su tr; do command -v "$c" >/dev/null || die "Missing utility: $c"; done
[ -x ./kptools ] && [ -x ./ksud ] || die "Run chmod +x kptools ksud."
su -c 'id' | grep -q 'uid=0' || die "FolkPatch root is not available."
printf '\nChecking genuine HEZB1 init_boot...\n'
printf '%s  %s\n' "$INIT_SHA" "original-init_boot.img" | sha256sum -c - || die "Original init_boot SHA256 mismatch."
printf '\nChecking on-device partitions still match backups...\n'
LIVE_BOOT="$(su -c 'sha256sum /dev/block/by-name/boot' | awk '{print $1}')"
LIVE_INIT="$(su -c 'sha256sum /dev/block/by-name/init_boot' | awk '{print $1}')"
COPY_BOOT="$(sha256sum physwizz-folkpatch-boot.img | awk '{print $1}')"
COPY_INIT="$(sha256sum init_boot-current-backup.img | awk '{print $1}')"
[ -n "$LIVE_BOOT" ] && [ "$LIVE_BOOT" = "$COPY_BOOT" ] || die "Live boot differs from saved boot backup."
[ -n "$LIVE_INIT" ] && [ "$LIVE_INIT" = "$COPY_INIT" ] || die "Live init_boot differs from saved init_boot backup."
[ "$(head -c 8 clean-physwizz-candidate.img)" = "ANDROID!" ] || die "Clean boot image has invalid magic."
[ "$(head -c 8 original-init_boot.img)" = "ANDROID!" ] || die "Original init_boot image has invalid magic."
printf '\nInspecting patched state of extracted kernel and repacked boot...\n'
./kptools -l -i kernel > kernel-unpatch-check.txt || die "Cannot inspect extracted kernel."
grep -q '^patched=false$' kernel-unpatch-check.txt || die "KernelPatch still detected in extracted kernel."
# kptools -l expects a kernel image, NOT an Android boot.img. Extract a fresh
# copy from the repacked boot into a dedicated directory, then inspect it.
mkdir -p repacked-boot-inspection
rm -f repacked-boot-inspection/kernel
(cd repacked-boot-inspection && "$WORK/kptools" unpack "$WORK/clean-physwizz-candidate.img") || die "Cannot extract kernel from repacked boot."
[ -s repacked-boot-inspection/kernel ] || die "Repacked boot has no extractable kernel."
cmp -s kernel repacked-boot-inspection/kernel || die "Repacked boot's extracted kernel differs from the unpatched candidate."
./kptools -l -i repacked-boot-inspection/kernel > boot-unpatch-check.txt || die "Cannot inspect extracted repacked kernel."
grep -q '^patched=false$' boot-unpatch-check.txt || die "KernelPatch still detected in repacked boot's extracted kernel."
[ "$(sha256sum clean-physwizz-candidate.img | awk '{print $1}')" != "$COPY_BOOT" ] || die "Clean boot is byte-identical to FolkPatch boot."
printf '\nDownloading Samsung RKP/DEFEX compatibility module...\n'
PHASE="download/patch"
curl -fL --retry 3 --retry-delay 1 -o kernelsu-samsung-compat.ko "$MOD_URL"
printf '%s  %s\n' "$MOD_SHA" "kernelsu-samsung-compat.ko" | sha256sum -c - || die "Samsung module SHA256 mismatch."
mkdir -p output
./ksud boot-patch --boot original-init_boot.img --module kernelsu-samsung-compat.ko --kmi android15-6.6 --out output --out-name init_boot-samsung-compat.img || die "KernelSU Next patching failed."
[ -s output/init_boot-samsung-compat.img ] || die "New init_boot missing."
[ "$(head -c 8 output/init_boot-samsung-compat.img)" = "ANDROID!" ] || die "New init_boot has invalid magic."
[ "$(sha256sum output/init_boot-samsung-compat.img | awk '{print $1}')" != "$INIT_SHA" ] || die "New init_boot is unchanged."
printf '\nChecking partition capacities...\n'
BOOT_CAP="$(su -c 'blockdev --getsize64 /dev/block/by-name/boot' | tr -d '\r')"
INIT_CAP="$(su -c 'blockdev --getsize64 /dev/block/by-name/init_boot' | tr -d '\r')"
BOOT_SIZE="$(stat -c %s clean-physwizz-candidate.img)"
INIT_SIZE="$(stat -c %s output/init_boot-samsung-compat.img)"
case "$BOOT_CAP:$INIT_CAP" in *[!0-9:]*|:*|*:) die "Could not read numeric partition capacities.";; esac
[ "$BOOT_SIZE" -eq "$BOOT_CAP" ] && [ "$INIT_SIZE" -eq "$INIT_CAP" ] || die "Images must equal full partition sizes for hash readback."
printf '\nStaging images into Downloads...\n'
mkdir -p "$STAGE"
cp clean-physwizz-candidate.img "$STAGE/boot-next.img"
cp output/init_boot-samsung-compat.img "$STAGE/init_boot-next.img"
cmp -s clean-physwizz-candidate.img "$STAGE/boot-next.img" || die "Boot copy mismatch."
cmp -s output/init_boot-samsung-compat.img "$STAGE/init_boot-next.img" || die "Init_boot copy mismatch."
printf '\nModule SHA256: %s\n' "$MOD_SHA"
printf 'Boot candidate: %s bytes. Init_boot candidate: %s bytes.\n' "$BOOT_SIZE" "$INIT_SIZE"
printf 'Backups: %s/{physwizz-folkpatch-boot.img,init_boot-current-backup.img}\n' "$WORK"
printf '\nWARNING: This candidate has never been tested on clean Physwizz at early boot. KDP is OFF.\n'
printf 'The checks cannot establish bootability or independent KernelSU Next root before reboot.\n'
printf 'Type FLASH A146P to write BOTH boot partitions (anything else aborts): '
IFS= read -r ANSWER
[ "$ANSWER" = "FLASH A146P" ] || die "Not confirmed; no partitions written."
PHASE="FLASHING boot/init_boot"
printf '\nWriting boot...\n'
su -c "dd if=$STAGE/boot-next.img of=/dev/block/by-name/boot bs=1048576 conv=fsync" || die "Boot write failed. DO NOT REBOOT."
printf 'Writing init_boot...\n'
su -c "dd if=$STAGE/init_boot-next.img of=/dev/block/by-name/init_boot bs=1048576 conv=fsync" || die "init_boot write failed. DO NOT REBOOT."
su -c sync || die "Sync failed. DO NOT REBOOT."
printf '\nChecking flashed partitions against staged images...\n'
NEW_BOOT="$(su -c 'sha256sum /dev/block/by-name/boot' | awk '{print $1}')"
NEW_INIT="$(su -c 'sha256sum /dev/block/by-name/init_boot' | awk '{print $1}')"
[ "$NEW_BOOT" = "$(sha256sum "$STAGE/boot-next.img" | awk '{print $1}')" ] || die "Flashed boot hash mismatch. DO NOT REBOOT."
[ "$NEW_INIT" = "$(sha256sum "$STAGE/init_boot-next.img" | awk '{print $1}')" ] || die "Flashed init_boot hash mismatch. DO NOT REBOOT."
PHASE="complete"
printf '\nBoth images written and hashes verified. DO NOT FLASH AGAIN.\n'
printf 'MANUAL NEXT: FolkPatch Manager -> Uninstall -> Remove AndroidPatch only and keep the Manager.\n'
printf 'THEN reboot and validate KernelSU Next Manager and su -c id in Termux, including after a second reboot.\n'
printf 'If boot fails, you need your original boot/init_boot backups for recovery. This script cannot rollback an unbootable phone.\n'