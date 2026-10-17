# SM-A146P HEZB1: Duck ToolBox KeyMint RKP method vs Samsung RKP and Play Integrity (2026-10-18)

Research-only source assessment for A146PXXUHEZB1 stock 6.6.89 and user's currently Physwizz-rooted SM-A146P. **No provisioning requests, device commands, Google certificate issuance, private-key extraction, keybox creation, module loading, or ROM changes were performed.**

## Two entirely different RKPs

1. **Samsung Knox Real-time Kernel Protection (RKP)** is a Samsung runtime kernel hardening system. KernelSU Next v3.4.2 has Samsung-specific RKP/KDP/DEFEX compatibility code. Its compatibility does not, by itself, attest genuine locked boot.
2. **Android Remote Key Provisioning (RKP)** is a KeyMint/DICE and Google certificate issuance protocol for Android hardware-backed attestation. Duck ToolBox's device issuer concerns this second RKP; it is **not** a fix for Samsung's kernel RKP.

## Kanxue original claim vs implementation

Original technical write-up: https://bbs.kanxue.com/thread-293244.htm (original Chinese). Its author describes a Qualcomm KeyMint trusted-app V2 request that accepts a **software-controlled** P-256 public key for a device-signed CSR without checking the expected generation provenance, then submits the CSR to the Google remote provisioning service. It claims a Google-signed attestation certificate chain and compatible `keybox.xml` were obtained on **the author's tested Qualcomm firmware**. The exploit property is implementation-specific and could be removed by TA or server fixes; it is not a proof for all Qualcomm or other vendors.

Implementation: https://github.com/eltavine/Duck-ToolBox, studied at Git SHA `fb6b1e427f2773ac6139d2eba27068fbdfd089de` (2026-10-17). Its `crates/duck-rkp-device/src/soc.rs` explicitly classifies Mediatek/MTK as `Vendor::Other` and produces blocker `qualcomm_soc_required` for non-Qualcomm hardware. `crates/duck-rkp-device/src/status.rs` and `service.rs` enforce this check. V2 expects Qualcomm `/dev/smcinvoke` + `/vendor/lib64/libkeymasterdeviceutils.so`; V1 AIDL/native fallbacks also retain the Qualcomm SoC guard and their own firmware ABI needs. Duck documents that a OnePlus PJX110 Android 16 test reached its TA but returned -18, producing no keybox; the V1 variants were not validated to issue production certificates on hardware in the cited README.

## User hardware is an incompatible SoC

SM-A146P uses **MediaTek MT6833 (Dimensity 700)**, corroborated by owner's `mt6833` vendor-module inventory and [Vodafone AU device specs](https://devices.vodafone.com.au/samsung/galaxy-a14-5g-android-13/specifications/). It is neither Qualcomm KeyMint nor the tested Qualcomm vendor trusted-app ABI. Installing the current Duck ToolBox does not make it compatible, and removing the Qualcomm guard without porting/validating the entire MediaTek secure component would not fix the protocol mismatch. **Do not execute the provisioning feature or assume a keybox will be created.**

## What obtaining a certificate would and would not prove

A successfully issued X.509 attestation chain shows that the applicable issuer accepted an attestation certificate request and signed the requested key. This is **not** equivalent to a Google Play Integrity `MEETS_STRONG_INTEGRITY` verdict. Google documents for Android 13+ that `MEETS_DEVICE_INTEGRITY` requires hardware-backed verified locked boot and a certified manufacturer OS image, while `MEETS_STRONG_INTEGRITY` additionally requires recent OS and vendor security updates. Hooking a Keystore/attestation API can affect what some clients see, but server-side labels are not guaranteed by possession of a certificate, nor does Samsung RKP hardening prove them.

Official documentation: https://developer.android.com/google/play/integrity/setup and https://source.android.com/docs/core/ota/modular-system/remote-key-provisioning

The post's phrase "no external server" must be understood as "no independent certificate-brokering service"; Google RKP endpoints remain involved. The keybox includes a **software-generated/exportable private key** and is sensitive; unlike true TEE-nonexportable keys, a software key is not cryptographically confined to the source phone merely because its CSR was device-signed. Avoid sharing keyboxes or private keys publicly.

## Next safe research path, preserving current phone

- Identify the actual MediaTek KeyMint/IRemotelyProvisionedComponent implementation and its public HAL protocol from original firmware artifacts or benign read-only metadata. AOSP's `com.android.rkpd` module delegates to OEM `IRemotelyProvisionedComponent`; Qualcomm's proprietary TA commands should not be inferred for MediaTek.
- For baseline measurement, use a recognized Play Integrity diagnostic to record actual app-side labels, plus the stock/Physwizz verified-boot state and patch dates, keeping secrets out of logs.
- Continue original goal separately: GhostLock static preflight for stock signed 6.6.89; original boot CRC matches 160/160 KSU Next exported imports plus `module_layout`, with 59 nonexported imports and runtime protection remaining unresolved.
- **No promise of Strong Integrity on unlocked Physwizz or post-exploit signed-stock device**, and no risky flashing/relocking or custom KeyMint operations.

Sources: original Kanxue post, official Duck ToolBox README and source at cited commit, Android RKP & Play Integrity official docs, and OEM device specification.
