# SM-A146P MediaTek MT6833 vs Duck ToolBox v0.1.6: grounded RKP status

**18 October 2026.** Purpose: determine whether the Duck ToolBox device RKP issuer can work on Samsung A14 5G (SM-A146P) with stock firmware A146PXXUHEZB1, while the phone *currently boots the Physwizz custom kernel*. This is a code/capability audit, not a provisioning experiment. No private keys or CSR artifacts should be collected/shared for this diagnostic.

## Exact upstream release and code

- Upstream Duck ToolBox release: https://github.com/eltavine/Duck-ToolBox/releases/tag/v0.1.6-stable (published 2026-10-17 18:34:39 UTC).
- Pinned source: https://github.com/eltavine/Duck-ToolBox/tree/v0.1.6-stable
- `crates/duck-rkp-device/src/soc.rs`: the vendor model recognizes `MediaTek` and `MTK` as `Vendor::Other`; `Detection::blocker` returns **`qualcomm_soc_required`**. Upstream test `known_other_vendors_are_distinct_from_unknown_values` checks this, and `conflicting_sources_are_reported_instead_of_choosing_the_first` tests the gate. SoC/platform substitution would NOT make the vendor KeyMint ABI appear.
- `crates/duck-rkp-device/src/status.rs`: `rkp-device status` runs without provisioning; it reports `android_arm64`, root, chipset evidence and blockers. The native V2 interface assumes `/vendor/lib64/libkeymasterdeviceutils.so` + `/dev/smcinvoke`. V1 uses a system-owned RKP APK with specific AIDL classes; native V1 reuses the Qualcomm vendor library/node. All modes currently retain the Qualcomm vendor gate.
- `crates/duck-rkp-device/src/keymint.rs`: calls `keymasterutils::KeymasterUtils` C++ ABI exported from the Qualcomm vendor library; no corresponding MediaTek adapter is implemented.
- `crates/duck-rkp-device/src/issuance.rs` offers `auto`, `v1`, `v2`, `v1-native`, but no MediaTek-specific backend. Upstream README explicitly describes the **Device RKP Issuer** as Qualcomm KeyMint only, including a failed hardware test on a OnePlus Qualcomm device (TA status `-18`) that produced no keybox.

## Separate capability vs unsupported feature

| Duck feature | A146P status |
|---|---|
| Duck ToolBox WebUI / module manager | Can be installed/tested independently of Qualcomm; not proof of Strong Integrity. |
| Tricky Store / TEESimulator / OhMyKeymint configuration interfaces | Cross-device management features; actual installed downstream plugins must be compatible and trustworthy. |
| General `rkp` workbench | Software/offline material-processing mode; upstream states device-acquisition/TEE firmware collection not implemented here. Import requires legitimate existing DICE/signing material not contained in boot/init_boot. |
| **`rkp-device provision` Qualcomm KeyMint issuer** | **Blocked by MediaTek MT6833 hardware classification**; cannot legitimately expect success using Qualcomm-specific native entrypoints. |
| Samsung KDP/RKP/DEFEX kernel compatibility from KernelSU Next | Different from Android Remote Key Provisioning. Kernel hook/credential mechanisms do not change KeyMint's TEE ABI. |

Android standard RKPD/AIDL services can exist on this Samsung independently of Duck's vendor-specific signing-oracle implementation. Their presence is not evidence that external software public keys can be certified or that Google accepts any resulting CSR.

## Safe next evidence collection

Read-only script added to our branch:
- `a146p-stock/tools/a146p-duck-rkp-readonly-preflight.sh`
- Mock MT6833 shell syntax and diagnostics [GitHub Actions #39066540947](https://github.com/wiredroid/Patch-Recovery/actions/runs/39066540947) **success**. This CI uses **synthetic** properties, not a real A146P runtime and performs no network/KeyMint calls.

One-line Termux read-only device inventory (requires no root):

```sh
curl -fL "https://raw.githubusercontent.com/wiredroid/Patch-Recovery/a146p-ksunext-stock-build/a146p-stock/tools/a146p-duck-rkp-readonly-preflight.sh" -o "$HOME/a146p-duck-rkp-readonly-preflight.sh" && sh "$HOME/a146p-duck-rkp-readonly-preflight.sh" | tee "/sdcard/Download/A146P-Duck-RKP-preflight.txt"
```

If official Duck ToolBox v0.1.6 is *already installed* as an approved root module, get its own side-effect-free prerequisite output:

```sh
su -c "/data/adb/modules/duck-toolbox/bin/duckd rkp-device status"
```

The `status` command does not call the KeyMint TA or the Google server. Do not use `provision` as an experiment on this unsupported chipset.

Do not upload private keyboxes, `*.key`, hardware attestation chains, or device serial identifiers to public GitHub/issues. Diagnostic report is limited to generic model/SoC/patch-level/service names, excludes identifiers/secret material.

## Trust requirements and realistic outcome

Google's current Play Integrity documentation (https://developer.android.com/google/play/integrity/verdicts) states that Android 13+ `MEETS_STRONG_INTEGRITY` depends on `MEETS_DEVICE_INTEGRITY` (hardware-backed locked bootloader and certified OS) and security patches within the last year for all partitions including OS/vendor. Providing a Keybox XML or loading a kernel root module is NOT a proof of those requirements. **Do not relock with a modified Physwizz boot image.**

For a MediaTek port, first identify the actual KeyMint HAL implementation/transport and whether a vendor-supported interface authorizes the requested operation; then validate security properties on test hardware. Never recast `qualcomm_soc_required` as a cosmetic flag, or claim device-backed issuance on MTK from a Qualcomm-only backend.

**Bottom line: generic Duck Toolbox features are suitable for device-specific compatibility diagnostics, but its currently published device RKP issuer cannot run as described on the SM-A146P MT6833.**


## Follow-up: upstream v0.1.6 AIDL V1 eligibility and read-only MT6833 probe

I reviewed the exact pinned `v0.1.6-stable` `soc.rs`, `status.rs`, `issuance.rs`, `keymint.rs`, `v1/discovery.rs`, and `RkpV1Bridge.java`. The Android AIDL V1 adapter references `android.hardware.security.keymint.IRemotelyProvisionedComponent/default`, `getHardwareInfo` and `generateCertificateRequest`. **It is NOT a generic arbitrary-key signing endpoint**; Duck’s V1 implementation assumes a Qualcomm PureSoft/zero-HBK behavior, and `issuance::blockers_for` never removes `qualcomm_soc_required` for explicit `--protocol v1` on MediaTek. The V2 and native V1 vendor commands still require Qualcomm KeymasterUtils and/or `/dev/smcinvoke`. Removing the SoC gate alone provides no functional MediaTek backend.

An additional [read-only diagnostic shell probe](../tools/a146p-duck-rkp-readonly-probe.sh) now captures only public SoC/Android metadata, detected hardware-library filenames and Binder service names. The script does not call trusted applications, manufacture keyboxes, query device serials, collect key material, or contact Google. Its POSIX shell syntax and a **synthetic MediaTek + Binder mock** passed [GitHub CI #39068294855](https://github.com/wiredroid/Patch-Recovery/actions/runs/39068294855).

**Run on the actual Physwizz-rooted phone without switching kernels** (Termux; no `su` needed for initial metadata):

```sh
curl -fL "https://raw.githubusercontent.com/wiredroid/Patch-Recovery/a146p-ksunext-stock-build/a146p-stock/tools/a146p-duck-rkp-readonly-probe.sh" -o "$HOME/a146p-duck-rkp-readonly-probe.sh" && sh "$HOME/a146p-duck-rkp-readonly-probe.sh" | tee "/sdcard/Download/A146P-Duck-RKP-probe.txt"
```

Collect `/sdcard/Download/A146P-Duck-RKP-probe.txt` to check whether an actual remotely-provisioned-component service exists, which HAL version it may use, and which KeyMint/TEE vendor files are visible. Rooted Physwizz runtime evidence **does not prove** how stock locked-boot firmware behaves. A visible standard Android RKP HAL indicates normal remote provisioning support, not a software-key-signing vulnerability. Any real MediaTek support must involve an independently established compatible, authorized KeyMint transport and verification of its security properties before provisioning can be considered.

Keep private keys, hardware attestation blobs, keybox.xml, CSR payloads and serial/IMEI out of shared reports. Neither Samsung Knox RKP support in KernelSU Next nor Duck’s attestation tooling guarantees Play Integrity Strong.
