# Duck ToolBox v0.1.4-stable / Android RKP feasibility on SM-A146P MT6833
18 October 2026. Research-stage **read-only** assessment; no device secret/key/certificate operations.

## Goal and critical distinction
User owns rooted Galaxy A14 5G `SM-A146P`, **MediaTek MT6833**, running Physwizz KernelSU Next, targeting original signed Samsung `A146PXXUHEZB1` stock kernel `6.6.89-android15-8-abA146PXXUHEZB1-4k` for separate locked-stock root work.

**Android Remote Key Provisioning (RKP)** produces attestable KeyMint certificates. **Samsung Real-time Kernel Protection (also RKP)** is an EL2/runtime kernel-hardening mechanism. They are not the same feature. Google's `MEETS_STRONG_INTEGRITY` is a separate server-verified Play Integrity verdict with certified stock OS, verified locked boot state and up-to-date patches; root/KeyMint/keybox alone cannot guarantee it.

## Exact upstream source review
Upstream: [eltavine/Duck-ToolBox v0.1.4-stable](https://github.com/eltavine/Duck-ToolBox/releases/tag/v0.1.4-stable), published 2026-10-17.

- `crates/duck-rkp-device/src/soc.rs`: `mediatek`, `mtk`, `samsung` classified as `Vendor::Other`; `Detection::blocker()` returns **`qualcomm_soc_required`**. On this actual MT6833 model Duck's RKP-device status/provision cannot be expected to pass.
- `status.rs`: native V2 requires both **`/vendor/lib64/libkeymasterdeviceutils.so`** and **`/dev/smcinvoke`**. These are **Qualcomm-specific**. Alternative AIDL V1 checks RKPD app + `app_process`, but device-wide Qualcomm check still blocks non-Qualcomm.
- `keymint.rs`: `dlopen` Qualcomm `KeymasterUtils` C++ mangled constructor/destructor/send_cmd ABI. No MediaTek transport implementation is present.
- `protocol.rs`: V2 vendor command `0x3122` accepts a CBOR `keysToSign` public key. V1-native command `0x311e` in `v1/native.rs` is also identified explicitly as a Qualcomm legacy path. An Android platform HAL being present does **not** establish Qualcomm's distinct vendor behavior on MTK.
- `service.rs` and `issuance.rs`: source architecture does separate protocol selection / artifact verification from vendor bridge, so **a specific independently validated MTK backend** could reuse validation and UI. However, a generic read-only MTK RKP HAL does not imply it can attest an externally generated software key. Standard Android `IRemotelyProvisionedComponent` requires valid MAC authentication for `MacedPublicKey[] keysToSign` and must reject invalid MACs.

Sources:
- [Duck SoC gate](https://github.com/eltavine/Duck-ToolBox/blob/v0.1.4-stable/crates/duck-rkp-device/src/soc.rs)
- [Duck native vendor library and driver requirements](https://github.com/eltavine/Duck-ToolBox/blob/v0.1.4-stable/crates/duck-rkp-device/src/status.rs)
- [Duck Qualcomm KeyMint C++ ABI](https://github.com/eltavine/Duck-ToolBox/blob/v0.1.4-stable/crates/duck-rkp-device/src/keymint.rs)
- [Standard AIDL remotely-provisioned HAL](https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/security/rkp/aidl/android/hardware/security/keymint/IRemotelyProvisionedComponent.aidl)
- [Google Play Integrity verdict requirements](https://developer.android.com/google/play/integrity/verdicts)

## Actual next action, no guesswork
Read-only phone probe: `a146p-stock/tools/a146p-duck-mtk-keymint-readonly-probe.py`, run once using existing Termux+KSU Next root. This collects only **service names**, safe Android properties (no full fingerprint, IMEI or serial), candidate vendor HAL filenames, device-node presence, known Qualcomm ABI prerequisites and RKPD package directory names.

Copyable Termux command:

```sh
curl -fL "https://raw.githubusercontent.com/wiredroid/Patch-Recovery/a146p-ksunext-stock-build/a146p-stock/tools/a146p-duck-mtk-keymint-readonly-probe.py" -o "$HOME/a146p-duck-mtk-probe.py" && su -c "/data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/a146p-duck-mtk-probe.py"
```

Expected output file: `/sdcard/Download/A146P-Duck-MediaTek-KeyMint-capabilities.json`. User should upload the report, not any private keys, keyboxes, attestations, CSR or certificate chain. Next step is to classify stock `IRemotelyProvisionedComponent` version/service and MTK KeyMint/TEE transport using **read-only inventory**; do not change vendor SELinux or run unknown vendor TEE operations on live firmware.

## Status
**Duck ToolBox KernelSU module may support other Workbench features on this phone, but `rkp-device provision` is not ported to MediaTek and cannot be honestly advertised as working on A146P.** Changing a `qualcomm_soc_required` boolean is not an adapter. The public research article specifically reports a vulnerable **Qualcomm KeyMint** firmware; no analogous MT6833 result has been verified. Do not promise Play Strong Integrity.
