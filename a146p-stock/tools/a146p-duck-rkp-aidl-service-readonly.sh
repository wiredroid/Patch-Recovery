#!/system/bin/sh
# SM-A146P Android Remote Key Provisioning Binder/VINTF presence diagnostic.
# READ-ONLY: no KeyMint call, TEE command, CSR, certificates, secrets,
# vendor props change, init_module, network provisioning or root escalation.
# Intended to run with EXISTING KernelSU root to minimize service visibility gaps.
set -u
printf '%s\n' 'A146P DUCK TOOLBOX — EXACT ANDROID RKP HAL DISCOVERY (READ ONLY)'
printf '%s\n' '================================================================'
printf '\n%s\n' '[Execution context]'
id -u 2>/dev/null || true
printf 'model=%s\n' "$(getprop ro.product.model 2>/dev/null)"
printf 'soc=%s\n' "$(getprop ro.soc.manufacturer 2>/dev/null)"
printf 'hardware=%s\n' "$(getprop ro.hardware 2>/dev/null)"
printf '\n%s\n' '[AIDL service registry — public service NAMES only]'
if command -v service >/dev/null 2>&1; then
  listing="$(service list 2>&1)"
  rc="$?"
  if [ "$rc" -eq 0 ]; then
    printf '%s\n' "$listing" | grep -iE 'IRemotelyProvisionedComponent|IKeyMintDevice|ISehKeyMint|remote_provision|rkpd' || printf '%s\n' 'NONE_VISIBLE (no exact RKP Binder service discovered)'
  else
    printf 'SERVICE_LIST_FAILED rc=%s\n' "$rc"
  fi
  printf '\n%s\n' '[Non-mutating checkService queries for expected RKP HAL names]'
  for name in \
    android.hardware.security.keymint.IRemotelyProvisionedComponent/default \
    android.hardware.security.keymint.IRemotelyProvisionedComponent/strongbox \
    android.hardware.security.keymint.IRemotelyProvisionedComponent/tee \
    android.hardware.security.keymint.IKeyMintDevice/default; do
    printf '%s : ' "$name"
    service check "$name" 2>&1 | head -n 3
  done
else
  printf '%s\n' 'SERVICE_TOOL_UNAVAILABLE'
fi
printf '\n%s\n' '[VINTF declarations — Android RKP and KeyMint only]'
hits=0
for file in \
  /vendor/etc/vintf/manifest.xml /vendor/etc/vintf/manifest/*.xml \
  /odm/etc/vintf/manifest.xml /odm/etc/vintf/manifest/*.xml \
  /system/etc/vintf/manifest.xml /system/etc/vintf/manifest/*.xml \
  /system_ext/etc/vintf/manifest.xml /system_ext/etc/vintf/manifest/*.xml \
  /product/etc/vintf/manifest.xml /product/etc/vintf/manifest/*.xml \
  /apex/*/etc/vintf/manifest.xml /apex/*/etc/vintf/manifest/*.xml; do
  [ -f "$file" ] || continue
  lines="$(grep -niE 'IRemotelyProvisionedComponent|IKeyMintDevice|ISehKeyMint|android.hardware.security.keymint|android.hardware.security.rkp|vendor.samsung.hardware.keymint' "$file" 2>/dev/null | head -n 45)"
  [ -n "$lines" ] || continue
  hits=$((hits+1))
  printf '%s\n%s\n' "--- $file" "$lines"
done
[ "$hits" -gt 0 ] || printf '%s\n' 'NO_VINTF_MATCH (searched vendor/odm/system/product and APEX)'
printf '\n%s\n' '[Duck AIDL V1 app prerequisites]'
for item in /system/bin/app_process /system/bin/app_process64; do
  [ ! -e "$item" ] || printf 'PRESENT %s\n' "$item"
done
for file in /apex/com.android.rkpd/priv-app/*/rkpdapp.apk /apex/com.android.rkpd/app/*/rkpdapp.apk; do
  [ ! -f "$file" ] || printf 'PRESENT %s\n' "$file"
done
printf '\n%s\n' '[Visible RKP-related installed package names, not app data]'
if command -v pm >/dev/null 2>&1; then
  pkgs="$(pm list packages 2>/dev/null)"
  printf '%s\n' "$pkgs" | grep -iE 'rkpd|remoteprovision' || printf '%s\n' 'NO_PACKAGE_MATCH (package visibility is not HAL availability)'
fi
printf '\n%s\n' '[Conclusions]'
printf '%s\n' 'Checking a Binder service name is not the same as calling KeyMint or requesting certificates.'
printf '%s\n' 'If no IRemotelyProvisionedComponent is registered or declared, Duck V1 AIDL bridge has no verified target.'
printf '%s\n' 'MediaTek remains excluded by Duck upstream qualcomm_soc_required gate, regardless of APK presence.'
printf '%s\n' 'No attestation keys, keybox, RKP CSR, Google requests, SELinux changes or module loading were attempted.'
