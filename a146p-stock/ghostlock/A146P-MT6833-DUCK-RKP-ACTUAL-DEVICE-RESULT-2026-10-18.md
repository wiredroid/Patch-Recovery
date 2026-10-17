# SM-A146P MT6833 — actual Duck ToolBox RKP read-only probe, 18 October 2026

## Confirmed physical device observation (not a simulation)

Owner ran [our read-only probe](../tools/a146p-duck-rkp-readonly-probe.sh) on the **Physwizz-rooted Samsung Galaxy A14 5G SM-A146P**, MediaTek MT6833, Android 15 API 35. The console printed:

- `ro.hardware=mt6833`, `ro.board.platform=mt6833`, `ro.soc.manufacturer=Mediatek`, `ro.product.cpu.abi=arm64-v8a`
- **Absent** `/dev/smcinvoke`, `/vendor/lib64/libkeymasterdeviceutils.so`, `/vendor/lib64/libQSEEComAPI.so`.
- **Present** `/system/bin/app_process`.
- Binder **visible** `android.hardware.security.keymint.IKeyMintDevice/default`, `vendor.samsung.hardware.keymint.ISehKeyMintExtension/default`, `vendor.samsung.hardware.keymint.ISehKeyMintFactory/default`.
- **Not listed** in the captured output: `android.hardware.security.keymint.IRemotelyProvisionedComponent/default` (not a definitive absence finding; could be lazy or access restricted).
- Vendor files include `android.hardware.security.keymint-V1-ndk.so`, `libskeymint10device.so`, `libskeymint_cli.so`, `libteecl.so`, and Samsung's vendor keymint AIDL library. Filename presence does not establish a usable arbitrary-key RKP backend.

**No device identifiers, attestation materials, private keys, CSR, keybox, trustlet calls, module insertion or firmware modifications were obtained or made.**

## Independently examined Duck ToolBox source (v0.1.6-stable)

- `crates/duck-rkp-device/src/soc.rs`: MediaTek/Samsung classified `Vendor::Other`; `blocker()` explicitly returns `qualcomm_soc_required`.
- `status.rs`: Qualcomm V2 requires `libkeymasterdeviceutils.so` and `/dev/smcinvoke`; AIDL V1 discovery is a separate path but does **not** eliminate the Qualcomm SoC gate.
- `v1/discovery.rs`: searches system-owned `rkpdapp.apk` in `/apex/com.android.rkpd` and `RemoteProvisioner.apk` in system paths. Probe showed no positive hit for these exact APKs; further inspection is warranted.
- `bridge/RkpV1Bridge.java`: requires Binder service `IRemotelyProvisionedComponent/default`, not `IKeyMintDevice/default` or `ISehKeyMintExtension/default`. Its V1 AIDL implementation is **not** a generalized arbitrary software-key certification feature.
- `v1/native.rs`: native V1 command `0x311e` is Qualcomm-specific. `keymint.rs`: V2 command `0x3122` uses Qualcomm KeymasterUtils and SMCI device path.
- `cli.rs`: feature describes itself as “Device-backed RKP issuance on compatible Qualcomm KeyMint firmware”.

**Result: Duck `rkp-device provision` is not presently supported on A146P; removing its Qualcomm gate is not a sufficient or safe port.** The regular Duck UI/other device-neutral tools are a different question.

## Actual next investigation / script published and CI tested

New read-only [`a146p-duck-rkp-vintf-readonly.sh`](../tools/a146p-duck-rkp-vintf-readonly.sh) checks VINTF HAL declarations, the exact registered `IRemotelyProvisionedComponent` service name, installed RKPD package names and Duck-recognized APK locations. Does not make Binder, TEE, RPC, Google, keybox or system-state-changing calls.

- [CI #39068724950](https://github.com/wiredroid/Patch-Recovery/actions/runs/39068724950): **success** (POSIX shell syntax and offline diagnostic-output test only; this is not a live Android test).
- User may optionally run one line in Termux:

```sh
curl -fL 'https://raw.githubusercontent.com/wiredroid/Patch-Recovery/a146p-ksunext-stock-build/a146p-stock/tools/a146p-duck-rkp-vintf-readonly.sh' -o "$HOME/a146p-duck-rkp-vintf-readonly.sh" && sh "$HOME/a146p-duck-rkp-vintf-readonly.sh" | tee "/sdcard/Download/A146P-Duck-RKP-VINTF-readonly.txt"
```

Interpret absent service versus declared-but-lazy service carefully. If vendor declares an RPC interface in VINTF, it proves standardized legitimate remote provisioning support, not ability to certify host-controlled keys or pass Play Strong Integrity.

Android Remote Key Provisioning (RKP) is not Samsung Real-time Kernel Protection (also RKP). On Android 15, Play `MEETS_STRONG_INTEGRITY` also requires `MEETS_DEVICE_INTEGRITY` hardware-backed locked/certified image and vendor/OS security patches within the last year, per [Google Play Integrity docs](https://developer.android.com/google/play/integrity/verdicts). The current Physwizz rooted/unlocked state is not itself evidence of these conditions. No keybox or signing-oracle extraction should be claimed from firmware library names.

**No request to flash, relock, alter vendor SELinux or execute Duck's `provision` on unsupported firmware.**

## Follow-up on actual VINTF/AIDL read-only output (18 Oct 2026, owner)

Owner executed `a146p-duck-rkp-vintf-readonly.sh`, which returned:
- Running kernel (only runtime context): `6.6.89-android15-8-g6560c1ca1f00-dirty-physwizz`.
- **No visible** `android.hardware.security.keymint.IRemotelyProvisionedComponent` Binder service name from unprivileged `service list`; not proof that a lazy or permission-restricted service does not exist.
- `/vendor/etc/vintf/manifest.xml` advertises `android.hardware.security.keymint.IKeyMintDevice/default` plus Samsung `ISehKeyMintExtension/default` and `ISehKeyMintFactory/default`. These do **not** implement or advertise `IRemotelyProvisionedComponent`.
- **Duck-recognized AIDL V1 APK IS PRESENT**: `/apex/com.android.rkpd/priv-app/rkpdapp@AP3A.240905.015.A2/rkpdapp.apk`. Earlier blanket report that no V1 AIDL APK was found is superseded by this successful, wildcard APEX-path discovery. This is an APK/resource presence check, not evidence that the HAL is running.
- `pm list packages` from the read-only shell did not list an RKPD package; APEX module presence is distinct from package-manager listing.

Upstream [Duck ToolBox at ecb55b0 (v0.1.6-stable)](https://github.com/eltavine/Duck-ToolBox/tree/ecb55b0a634d13fad472d6707ae13ce6197cb360):
- `crates/duck-rkp-device/src/status.rs`: v1_available is true when system-owned RKPD APK and `/system/bin/app_process` exist; Qualcomm SoC is still a separate mandatory blocker.
- `crates/duck-rkp-device/src/issuance.rs`: **explicit `--protocol v1` does not remove `qualcomm_soc_required`** from the status blocker list.
- `crates/duck-rkp-device/bridge/RkpV1Bridge.java`: uses `ServiceManager.checkService("android.hardware.security.keymint.IRemotelyProvisionedComponent/default")` and calls its V1 methods. Without that actual service/interface the AIDL bridge cannot operate. Samsung `IKeyMintDevice/default` is not a substitute.
- `crates/duck-rkp-device/src/v1/mod.rs`: assumes a particular legacy PureSoft/zero-HBK AIDL V1 MAC behavior; a generic MediaTek port is not a safe simple SoC bypass.

### Concrete next diagnostic (read-only, using existing rooted Physwizz; never invoke provisioning)

Added `a146p-stock/tools/a146p-duck-rkp-aidl-service-readonly.sh` that runs name-only Binder `service list` and non-mutating `service check` for exact RKP HAL instance names, reads vendor/system/APEX VINTF XML names and RKPD APK paths, and reports only non-sensitive identification. **No TA calls, keys, certificates or provisioning.** [Syntax/lint CI #39070556444](https://github.com/wiredroid/Patch-Recovery/actions/runs/39070556444) **passed**; the actual live-device report must come from user.

Termux single line, writes a local report:
```sh
curl -fL "https://raw.githubusercontent.com/wiredroid/Patch-Recovery/a146p-ksunext-stock-build/a146p-stock/tools/a146p-duck-rkp-aidl-service-readonly.sh" -o "$HOME/a146p-duck-rkp-aidl-check.sh" && su -c "/system/bin/sh /data/data/com.termux/files/home/a146p-duck-rkp-aidl-check.sh" | tee "/sdcard/Download/A146P-Duck-RKP-AIDL-HAL-check.txt"
```

**Key limitation:** Even a registered legitimate Android Remote Key Provisioning HAL does not establish an exposed interface to attest arbitrary software-generated private keys, nor does it establish that a custom-rooted/unlocked Android 15 device meets `MEETS_STRONG_INTEGRITY`. Google requires hardware-backed locked/certified boot evidence and current OS/vendor patch levels. Android RKP and Samsung Real-time Kernel Protection are completely different features.
