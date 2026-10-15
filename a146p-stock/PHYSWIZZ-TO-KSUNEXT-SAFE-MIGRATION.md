# A146P Physwizz 6.6.89 → independent KernelSU Next 3.4.2: SAFE migration gate

**This document is NOT a flashing recipe.** Branch `a146p-ksunext-stock-build` only. Device: Samsung Galaxy A14 5G SM-A146P, currently reportedly running a patched Physwizz 6.6.89 kernel on an unlocked bootloader, rooted through FolkPatch/APatch-style patch.

## Known concrete components

- A KernelSU Next 3.4.2 LKM was previously manually loaded on the **Physwizz 6.6.89** running device. The proven experimental artifact is named `kernelsu-a146p-physwizz-6.6.89-EXPERIMENTAL.ko`, SHA-256 `5cc15a04c736982c4e5d7a025c67920dcd9aa45957503f0d90405f3b038acf07`. It is NOT validated against stock Samsung kernel. Proven only with existing APatch/FolkPatch privileges and not as an independent early-boot module.
- Direct release (experimental only): https://github.com/wiredroid/Patch-Recovery/releases/tag/a146p-ksunext-physwizz-6.6.89-exp1
- Official KernelSU Next manager **v3.4.2 / 33355** and corresponding `ksud`: https://github.com/KernelSU-Next/KernelSU-Next/releases/tag/v3.4.2 ; prefer unsPoofed manager; do not confuse with prior KSU 0.9.5.
- Original genuine Samsung **HEZB1 stock boot.img** SHA-256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`; original stock `init_boot.img` SHA-256 `a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976`. This **stock boot** is NOT the clean Physwizz boot needed for a pure Physwizz kernel migration. Both OEM stock images must stay unchanged for the *later* stock locked-BL project.
- Physwizz public releases https://github.com/physwizz/a146p/releases include `V-UI` / `V-UI-ksu` Linux 6.6.89 **Android 15 binary I**. `V-UI-ksu` incorporates **older KernelSU 0.9.5**, not Next 3.4.2. The user's reported firmware `A146PXXUHEZB1` has **binary H**. DO NOT blindly flash binary-I release on binary-H device, assume that any Physwizz release is the exact currently running kernel, or downgrade Samsung bootloader. Release notes describe signed boot, but they do NOT confer OEM trust to an unlocked/locked verified boot chain.

## Why an early-boot transition needs BOTH images

- FolkPatch/APatch modifies kernel content in `boot`. Merely loading KernelSU Next with FolkPatch-root privileges after Android boots does **not** make KernelSU independent.
- For standard KernelSU LKM mode, `ksud boot-patch` patches the **ramdisk**, usually `init_boot` on Android 15, to arrange early module loading. KernelSU Next supports an explicit `-m <known LKM>` input and `-b <unmodified source init_boot.img>`. See https://github.com/KernelSU-Next/KernelSU-Next/blob/dev/userspace/ksud/src/boot_patch.rs and https://kernelsu.org/guide/installation.html
- Independent migration also requires the **currently compatible unmodified Physwizz 6.6.89 kernel in boot.img** (no FolkPatch/APatch kernel patches or another root driver), plus KernelSU Next-patched `init_boot.img`. The exact correct clean Physwizz image is **NOT verified available** yet.
- Samsung devices commonly require Odin/Download mode recovery and may not support `fastboot boot`. Do not recommend fastboot as a blanket A146P procedure. Any unsigned boot and init_boot modification is only contemplated with an unlocked bootloader.
- Compatibility of the experimental KSU LKM with the **clean** Physwizz boot kernel without FolkPatch modifications, early-boot symbol resolution, and old `/data/adb` state MUST still be proven.

## Safe read-only first action (no flashing)

Connect phone to host with debugging enabled and approve ADB prompt, then run `bash a146p-stock/ksunext-next-migration-preflight.sh`.
Or use these individual terminal commands:

```sh
adb shell uname -r
adb shell getprop ro.boot.bootloader
adb shell getprop ro.boot.slot_suffix
adb shell getprop ro.boot.vbmeta.device_state
adb shell getprop ro.boot.verifiedbootstate
adb shell "su -c 'id'"
adb shell "su -c 'sha256sum /dev/block/by-name/boot /dev/block/by-name/init_boot'"
```

The script reads information only; no image is written.

## Candidate creation — HOLD FOR VERIFICATION

After comparing the device's real current bootloader revision and running Physwizz image, obtain and SHA-256 record:
1. Full current **APatch/FolkPatch-patched Physwizz boot** backup, full current init_boot backup, and original **CLEAN** Physwizz boot matching the actual kernel. A saved original Samsung stock boot is NOT interchangeable.
2. Exact original `init_boot` from that firmware and the previously working Physwizz KernelSU Next v3.4.2 `.ko`.
3. Odin recovery setup, verified recovery media, data backup, and understanding that Android root-manager coexistence or early startup failures could soft-brick/bootloop.

Then the official `ksud boot-patch` CLI can produce an OFFLINE candidate `init_boot` (using `-b`, `-m`, `--kmi android15-6.6`, and an output directory, **without** `-f`/flash). This has NOT yet been performed. The image must be inspected, its new SHA recorded, and planned alongside the separately verified clean Physwizz boot image. Avoid installing a standard GKI module, changing to stock 6.6.89 boot with a Physwizz `.ko`, or altering AVB/bootloader locks.
**No attempt to flash either image should proceed before a tested rollback and explicit user approval.**

After booting both *verified* candidates (if approved), validate the running kernel release, independent KSU root grants, module and manager version, and **absence** of APatch/KPatch/FolkPatch boot patches before calling the migration complete. Only then retire old root management; do NOT preemptively wipe `/data/adb`.

## Blockers as of 2026-10-16

- Device's **actual** current bootloader revision and current active boot hash not yet reconfirmed in this conversation.
- Exact unpatched Physwizz boot image for currently installed kernel/firmware not established.
- Offline patched init_boot candidate not created/validated.
- KernelSU Next persistent independent early boot not demonstrated.
- Stock locked-bootloader migration remains a **separate** objective requiring stock signed binaries and separately verified live privileges.

The only user-action requested now is to provide the **read-only preflight output** and identify an exact clean Physwizz `boot.img` matching the kernel actually running.
