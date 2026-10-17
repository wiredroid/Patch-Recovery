#!/system/bin/sh
# Read-only Device RKP / KeyMint discovery for SM-A146P (MediaTek MT6833).
# Does NOT contact Google, call a trusted application, request a CSR,
# generate keys, provision certificates, modify properties, or access secrets.
# No root needed. Does not print unique device IDs or full build fingerprint.
set -u
printf '%s\n' 'A146P DUCK TOOLBOX — READ-ONLY KEYMINT/RKP PROBE'
printf '%s\n' '=============================================='
prop() {
  key="$1"
  val="$(getprop "$key" 2>/dev/null)"
  [ -n "$val" ] || val='(missing)'
  printf '%s=%s\n' "$key" "$val"
}
for key in ro.product.model ro.hardware ro.boot.hardware ro.board.platform ro.soc.manufacturer ro.soc.model ro.vendor.soc.manufacturer ro.vendor.soc.model ro.product.cpu.abi ro.build.version.sdk; do prop "$key"; done
printf '\n%s\n' '[Qualcomm-specific Duck requirements]'
for path in /dev/smcinvoke /vendor/lib64/libkeymasterdeviceutils.so /vendor/lib64/libQSEEComAPI.so; do
  if [ -e "$path" ]; then
    printf 'PRESENT %s\n' "$path"
  else
    printf 'ABSENT  %s\n' "$path"
  fi
done
printf '\n%s\n' '[Android AIDL V1 prerequisites]'
if [ -f /system/bin/app_process ]; then
  echo 'PRESENT /system/bin/app_process'
else
  echo 'ABSENT  /system/bin/app_process'
fi
for path in \
  /apex/com.android.rkpd/priv-app/rkpd/rkpdapp.apk \
  /apex/com.android.rkpd/app/rkpd/rkpdapp.apk \
  /system/priv-app/RemoteProvisioner/RemoteProvisioner.apk \
  /system/app/RemoteProvisioner/RemoteProvisioner.apk \
  /system_ext/priv-app/RemoteProvisioner/RemoteProvisioner.apk; do
  if [ -f "$path" ]; then printf 'PRESENT %s\n' "$path"; fi
done
printf '\n%s\n' '[Binder KeyMint / Remote Provisioning service names]'
if command -v service >/dev/null 2>&1; then
  binder="$(service list 2>&1)"
  if [ "$?" -eq 0 ]; then
    printf '%s\n' "$binder" | grep -iE 'IRemotelyProvisionedComponent|IKeyMintDevice|IKeymasterDevice|keymaster|keymint' || echo 'NO_MATCH in service list (visibility may be limited)'
  else
    echo 'service list failed or was denied'
  fi
else
  echo 'service command not available'
fi
printf '\n%s\n' '[Potential vendor HAL component filenames, names only]'
for dir in /vendor/bin/hw /vendor/lib64/hw /vendor/lib64 /odm/bin/hw; do
  if [ -d "$dir" ]; then
    echo "-- $dir"
    ls -1 "$dir" 2>/dev/null | grep -iE 'keymint|keymaster|remoteprov|strongbox|trustonic|tee|mtee|tbase|rpmb' | head -n 50 || true
  fi
done
printf '\n%s\n' '[Result]'
echo 'These are local capability hints only; no KeyMint TA operation occurred.'
echo 'Qualcomm CSR_V2 0x3122 and native V1 0x311e are not portable to MediaTek.'
echo 'Even an AIDL V1 service cannot prove externally supplied keys will be accepted.'
echo 'No claim of Tricky Store / Play Integrity Strong attestation.'
