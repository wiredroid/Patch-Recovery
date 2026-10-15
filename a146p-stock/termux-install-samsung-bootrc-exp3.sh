#!/data/data/com.termux/files/usr/bin/bash
# A146P KernelSU Next Samsung boot-stage EXPERIMENTAL candidate installer.
# Flashes ONLY init_boot, and reboots ONLY after verified write.
# DO NOT use if you cannot recover an unbootable init_boot.
set -Eeuo pipefail
umask 077

WORK="$HOME/a146p-migration"
STAGE="/sdcard/Download/a146p-migration"
REPO="wiredroid/Patch-Recovery"
RUN_ID=38817636453
ART_NAME="A146P-Physwizz-6.6.89-Samsung-bootrc-UNTESTED"
KO_NAME="ksu-next-physwizz-6.6.89-samsung-bootrc-UNTESTED.ko"
CLEAN_BOOT_SHA="fe5823b91900254edac8e3446279f41197b9dccff4d4a17874ff9df5d455ac09"
ORIG_INIT_SHA="a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976"
PHASE="preflight"
fatal() { printf '\nSTOP [%s]: %s\n' "$PHASE" "$*" >&2; exit 1; }
trap 'printf "\nFAILED [%s] at line %s; DO NOT REBOOT IF A WRITE WAS STARTED AND NOT VERIFIED.\n" "$PHASE" "$LINENO" >&2' ERR
printf '\nA146P KernelSU Next Samsung boot RC EXP3 — UNTESTED, can cause a bootloop.\n'
[ "$(getprop ro.product.model)" = "SM-A146P" ] || fatal "Not SM-A146P"
[ "$(getprop ro.build.version.release)" = "15" ] || fatal "Not Android 15"
case "$(uname -r)" in 6.6.89*physwizz*) ;; *) fatal "Not expected Physwizz kernel";; esac
[ -s "$WORK/original-init_boot.img" ] && [ -s "$WORK/output/init_boot-samsung-compat.img" ] && [ -x "$WORK/ksud" ] || fatal "Original init_boot, running init_boot backup, or ksud missing."
for cmd in curl sha256sum awk grep sed dd stat cmp cp sleep su sync head wc; do command -v "$cmd" >/dev/null || fatal "Missing $cmd (install it in Termux first)"; done
if ! command -v unzip >/dev/null 2>&1; then pkg install -y unzip || fatal "Could not install unzip"; fi
printf '%s  %s\n' "$ORIG_INIT_SHA" "$WORK/original-init_boot.img" | sha256sum -c - || fatal "Stock init_boot hash mismatch."
su -c id | grep -q 'uid=0' || fatal "No root available."
LIVE_BOOT="$(su -c 'sha256sum /dev/block/by-name/boot' | awk '{print $1}')"
[ "$LIVE_BOOT" = "$CLEAN_BOOT_SHA" ] || fatal "boot partition differs from expected clean Physwizz. No writes."
LIVE_INIT="$(su -c 'sha256sum /dev/block/by-name/init_boot' | awk '{print $1}')"
CURRENT_INIT="$(sha256sum "$WORK/output/init_boot-samsung-compat.img" | awk '{print $1}')"
[ "$LIVE_INIT" = "$CURRENT_INIT" ] || fatal "init_boot differs from existing verified KernelSU Next image. No writes."
[ "$(stat -c %s "$WORK/output/init_boot-samsung-compat.img")" = 8388608 ] || fatal "Saved init_boot is not 8 MiB."
mkdir -p "$STAGE" "$WORK/output"
cp "$WORK/output/init_boot-samsung-compat.img" "$STAGE/init_boot-before-bootrc.img"
printf '\nWaiting for exact GitHub Actions run %s to PASS (up to 60 minutes)...\n' "$RUN_ID"
PHASE="wait for CI"
passed=0
for ((i=0; i<60; i++)); do
    result="$(curl -fLsS --connect-timeout 12 --max-time 25 --retry 2 -H 'Accept: application/vnd.github+json' "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID")" || fatal "Could not check CI status."
    if printf '%s' "$result" | grep -Eq '"conclusion"[[:space:]]*:[[:space:]]*"success"'; then
        passed=1
        break
    fi
    if printf '%s' "$result" | grep -Eq '"conclusion"[[:space:]]*:[[:space:]]*"(failure|cancelled|timed_out|skipped|action_required)"'; then
        fatal "GitHub Actions CI failed/cancelled. No writes. Inspect https://github.com/$REPO/actions/runs/$RUN_ID"
    fi
    [ $(( i % 5 )) -ne 0 ] || printf 'CI still running... (%s seconds)\n' "$(( i * 60 ))"
    sleep 60
done
[ "$passed" = 1 ] || fatal "Timed out waiting for CI; no writes."
PHASE="download & validate artifact"
printf '\nCI passed. Downloading built LKM artifact...\n'
ART_META="$(curl -fLsS --retry 2 -H 'Accept: application/vnd.github+json' "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID/artifacts")" || fatal "Could not get GitHub artifact digest"
printf '%s' "$ART_META" | grep -Fq "$ART_NAME" || fatal "Exact CI artifact not found"
ART_SHA="$(printf '%s' "$ART_META" | grep -oE '"digest"[[:space:]]*:[[:space:]]*"sha256:[0-9a-f]{64}"' | head -n 1 | sed -E 's/.*sha256:([0-9a-f]{64}).*/\1/')"
[ "$(printf %s "$ART_SHA" | wc -c)" = 64 ] || fatal "Missing GitHub SHA256 artifact digest"
curl -fL --retry 4 --retry-delay 3 --connect-timeout 15 --max-time 180 "https://nightly.link/$REPO/actions/runs/$RUN_ID/$ART_NAME.zip" -o "$WORK/bootrc-exp3-artifact.zip" || fatal "Artifact download failed; no writes."
printf '%s  %s\n' "$ART_SHA" "$WORK/bootrc-exp3-artifact.zip" | sha256sum -c - || fatal "GitHub archive digest mismatch."
unzip -t "$WORK/bootrc-exp3-artifact.zip" >/dev/null || fatal "Bad artifact zip."
unzip -p "$WORK/bootrc-exp3-artifact.zip" "out/$KO_NAME" > "$WORK/bootrc-exp3.ko" || fatal "Artifact has no expected .ko"
[ "$(stat -c %s "$WORK/bootrc-exp3.ko")" -gt 1000000 ] || fatal "Extracted .ko is unexpectedly small."
unzip -p "$WORK/bootrc-exp3-artifact.zip" "report/module-sha256.txt" > "$WORK/bootrc-exp3-module-sha256.txt" || fatal "Missing module hash report"
EXPECTED="$(awk '$2 ~ /samsung-bootrc-UNTESTED\.ko$/ && length($1) == 64 {print $1}' "$WORK/bootrc-exp3-module-sha256.txt" | head -n 1)"
[ "$(printf %s "$EXPECTED" | wc -c)" = 64 ] || fatal "Missing expected SHA256 in CI report"
ACTUAL="$(sha256sum "$WORK/bootrc-exp3.ko" | awk '{print $1}')"
[ "$EXPECTED" = "$ACTUAL" ] || fatal "Module SHA256 mismatch."
printf 'Kernel module verified SHA256: %s\n' "$ACTUAL"
PHASE="build replacement init_boot"
"$WORK/ksud" boot-patch --boot "$WORK/original-init_boot.img" --module "$WORK/bootrc-exp3.ko" --kmi android15-6.6 --out "$WORK/output" --out-name init_boot-bootrc-exp3.img || fatal "ksud boot-patch failed"
IMAGE="$WORK/output/init_boot-bootrc-exp3.img"
[ -s "$IMAGE" ] && [ "$(head -c 8 "$IMAGE")" = "ANDROID!" ] || fatal "Invalid patched init_boot"
[ "$(stat -c %s "$IMAGE")" = 8388608 ] || fatal "Patched init_boot size is not 8 MiB."
NEW_SHA="$(sha256sum "$IMAGE" | awk '{print $1}')"
[ "$NEW_SHA" != "$CURRENT_INIT" ] && [ "$NEW_SHA" != "$ORIG_INIT_SHA" ] || fatal "Patched image was unchanged."
cp "$IMAGE" "$STAGE/init_boot-bootrc-exp3.img"
cmp -s "$IMAGE" "$STAGE/init_boot-bootrc-exp3.img" || fatal "Staged image copy differs."
[ "$(su -c 'sha256sum /dev/block/by-name/init_boot' | awk '{print $1}')" = "$CURRENT_INIT" ] || fatal "Live init_boot changed while preparing; no writes."
PHASE="FLASH init_boot"
printf '\nFLASHING INIT_BOOT ONLY — UNTESTED Samsung boot-stage driver. Current backup: %s/init_boot-before-bootrc.img\n' "$STAGE"
su -c "dd if=$STAGE/init_boot-bootrc-exp3.img of=/dev/block/by-name/init_boot bs=1048576 conv=fsync" || fatal "INIT_BOOT WRITE FAILED. DO NOT REBOOT."
su -c sync || fatal "sync failed. DO NOT REBOOT."
FLASHED="$(su -c 'sha256sum /dev/block/by-name/init_boot' | awk '{print $1}')"
if [ "$FLASHED" != "$NEW_SHA" ]; then
    printf '\nHASH MISMATCH. Attempting restoration before reboot...\n' >&2
    su -c "dd if=$STAGE/init_boot-before-bootrc.img of=/dev/block/by-name/init_boot bs=1048576 conv=fsync" || fatal "Restoration failed; DO NOT REBOOT."
    su -c sync
    RESTORED="$(su -c 'sha256sum /dev/block/by-name/init_boot' | awk '{print $1}')"
    [ "$RESTORED" = "$CURRENT_INIT" ] || fatal "Restored readback mismatch; DO NOT REBOOT."
    fatal "Flash verification failed; restored old init_boot, no reboot."
fi
PHASE="complete"
printf '\nINIT_BOOT FLASH AND READBACK VERIFIED. Rebooting now...\n'
su -c reboot
