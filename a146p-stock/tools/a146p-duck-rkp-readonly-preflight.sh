#!/system/bin/sh
# Galaxy A14 5G SM-A146P - Duck ToolBox / MediaTek RKP compatibility diagnostic.
# Read-only: no su request, KeyMint TA call, Google network request, writes,
# keybox generation, attestation key extraction, system property changes or module load.
set -u
export LC_ALL=C
printf '%s\n' '=== SM-A146P / DUCK TOOLBOX READ-ONLY RKP PREFLIGHT ==='
printf '%s\n' 'This is a metadata inventory, NOT a provisioning attempt.'
printf 'Kernel currently running: '
uname -r 2>/dev/null || printf '%s\n' unavailable
printf '\n%s\n' '[build and SoC properties]'
for prop in \
  ro.product.model \
  ro.soc.manufacturer \
  ro.vendor.soc.manufacturer \
  ro.soc.model \
  ro.vendor.soc.model \
  ro.hardware \
  ro.boot.hardware \
  ro.board.platform \
  ro.build.version.release \
  ro.build.version.sdk \
  ro.build.version.security_patch \
  ro.vendor.build.security_patch \
  ro.boot.verifiedbootstate \
  ro.boot.flash.locked
do
  value="$(getprop "$prop" 2>/dev/null || true)"
  if [ -n "$value" ]; then printf '%s = %s\n' "$prop" "$value"; fi
done

printf '\n%s\n' '[Duck Qualcomm V2 prerequisites]'
for p in /dev/smcinvoke /vendor/lib64/libkeymasterdeviceutils.so; do
  if [ -e "$p" ]; then printf 'present: %s\n' "$p"
  else printf 'absent:  %s\n' "$p"; fi
done

printf '\n%s\n' '[MediaTek / standard KeyMint vendor HAL executables and libraries]'
found=0
for p in \
  /vendor/lib64/hw/*keymint*.so \
  /vendor/lib64/hw/*keymaster*.so \
  /vendor/lib64/*keymint*.so \
  /vendor/lib64/*keymaster*.so \
  /vendor/bin/hw/*keymint* \
  /vendor/bin/hw/*keymaster* \
  /odm/lib64/hw/*keymint*.so
do
  if [ -e "$p" ]; then
    printf 'present: %s\n' "$p"
    found=1
  fi
done
if [ "$found" -eq 0 ]; then
  printf '%s\n' 'No matching libraries found in this limited path inventory.'
fi

printf '\n%s\n' '[registered KeyMint / RKP Binder services]'
if command -v service >/dev/null 2>&1; then
  service list 2>/dev/null | grep -Ei 'keymint|keymaster|remotelyprovisioned' | head -25 || true
else
  printf '%s\n' 'service command unavailable'
fi
printf '\n%s\n' '[RKP app packages and APK candidates]'
if command -v pm >/dev/null 2>&1; then
  pm list packages 2>/dev/null | grep -Ei '(rkpd|remoteprovision)' | head -12 || true
fi
for p in /apex/com.android.rkpd/priv-app/*/rkpdapp.apk \
         /apex/com.android.rkpd/app/*/rkpdapp.apk \
         /system/priv-app/RemoteProvisioner/RemoteProvisioner.apk; do
  if [ -f "$p" ]; then printf 'RKP APK: %s\n' "$p"; fi
done

printf '\n%s\n' '[Duck module installation]'
if [ -e /data/adb/modules/duck-toolbox/module.prop ]; then
  printf '%s\n' 'Duck module location exists (may require root to inspect).'
else
  printf '%s\n' 'Duck module location not visible here (absent OR private to root).'
fi
printf '\n%s\n' '[interpretation]'
printf '%s\n' 'Duck ToolBox 0.1.6 rkp-device currently requires Qualcomm; MediaTek MT6833 is a chipset blocker.'
printf '%s\n' 'Standard Android KeyMint or RKPD presence DOES NOT mean Duck Qualcomm signing-oracle calls work.'
printf '%s\n' 'Samsung RKP kernel security and Android Remote Key Provisioning have different meanings.'
printf '%s\n' 'No private keys, CSR or attestation certificates are collected by this script.'
printf '%s\n' 'Do not relock a modified boot image or load unverified .ko files.'
