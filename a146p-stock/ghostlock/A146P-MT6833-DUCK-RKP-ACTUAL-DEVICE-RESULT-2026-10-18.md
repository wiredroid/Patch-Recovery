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
