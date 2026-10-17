#!/system/bin/sh
# Samsung A146P MT6833 KeyMint RKP VINTF/RKPD presence inventory.
# READ-ONLY: service names, HAL declaration paths, and APK paths only.
# No TA/Binder operations, no certificates, CSR, keys, properties writes,
# device identifiers, boot patches, network requests or module loading.
set -u
printf '%s\n' 'A146P DUCK RKP — VINTF/AIDL READ-ONLY FOLLOW-UP'
printf '%s\n' '==========================================='

printf '\n%s\n' '[Running kernel version — diagnostic context only]'
uname -r 2>/dev/null || true

printf '\n%s\n' '[Exact registered AIDL Remote Provisioning services]'
service_result="$(service list 2>&1)"
service_rc="$?"
if [ "$service_rc" -eq 0 ]; then
  printf '%s\n' "$service_result" | grep -i 'IRemotelyProvisionedComponent' || printf '%s\n' 'NONE_VISIBLE: IRemotelyProvisionedComponent (not proof of absent HAL)'
else
  printf 'service list denied or unavailable (exit=%s)\n' "$service_rc"
fi

printf '\n%s\n' '[VINTF XML HAL interface declarations, filenames and relevant lines]'
vintf_seen=0
for file in \
  /vendor/etc/vintf/manifest.xml /vendor/etc/vintf/manifest/*.xml \
  /odm/etc/vintf/manifest.xml /odm/etc/vintf/manifest/*.xml \
  /system/etc/vintf/manifest.xml /system/etc/vintf/manifest/*.xml \
  /system_ext/etc/vintf/manifest.xml /system_ext/etc/vintf/manifest/*.xml \
  /product/etc/vintf/manifest.xml /product/etc/vintf/manifest/*.xml; do
  [ -f "$file" ] || continue
  if grep -qiE 'IRemotelyProvisionedComponent|android.hardware.security.keymint|vendor.samsung.hardware.keymint' "$file" 2>/dev/null; then
    vintf_seen=1
    printf '%s\n' "--- $file"
    grep -niE 'IRemotelyProvisionedComponent|IKeyMintDevice|android.hardware.security.keymint|vendor.samsung.hardware.keymint|ISehKeyMint' "$file" 2>/dev/null | head -n 50 || true
  fi
done
[ "$vintf_seen" -eq 1 ] || printf '%s\n' 'NO_MATCH: relevant VINTF declarations not visible in searched paths'

printf '\n%s\n' '[Installed RKP packages (names only)]'
if command -v pm >/dev/null 2>&1; then
  packages="$(pm list packages 2>/dev/null)"
  if [ -n "$packages" ]; then
    printf '%s\n' "$packages" | grep -iE 'rkpd|remoteprovision' || echo 'NONE_VISIBLE: RKPD app package'
  else
    printf '%s\n' 'PACKAGE_MANAGER_UNAVAILABLE_OR_RESTRICTED'
  fi
fi

printf '\n%s\n' '[Duck AIDL V1 RKP APK discovery — system-owned filenames]'
rkp_apks=0
for dir in /apex/com.android.rkpd/priv-app/* /apex/com.android.rkpd/app/*; do
  if [ -f "$dir/rkpdapp.apk" ]; then
    printf 'PRESENT %s\n' "$dir/rkpdapp.apk"
    rkp_apks=1
  fi
done
for file in \
  /system/priv-app/RemoteProvisioner/RemoteProvisioner.apk \
  /system/app/RemoteProvisioner/RemoteProvisioner.apk \
  /system_ext/priv-app/RemoteProvisioner/RemoteProvisioner.apk; do
  if [ -f "$file" ]; then
    printf 'PRESENT %s\n' "$file"
    rkp_apks=1
  fi
done
[ "$rkp_apks" -eq 1 ] || echo 'NO_MATCH: Duck-recognized AIDL V1 APK'

printf '\n%s\n' '[Interpretation]'
echo 'Duck rkp-device current source still requires Qualcomm SoC, even with AIDL V1.'
echo 'RPC service declaration/presence alone is NOT proof of callable HAL or keybox issuance.'
echo 'This test performed no KeyMint/TEE/RKP requests and did not modify the phone.'
