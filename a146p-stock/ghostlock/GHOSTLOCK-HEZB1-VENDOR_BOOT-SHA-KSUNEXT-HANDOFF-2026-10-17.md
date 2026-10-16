# A146P GhostLock / KernelSU Next staged loader audit — 2026-10-17

## Newly verified by owner on running rooted A146P
```sh
su -c 'sha256sum /dev/block/by-name/vendor_boot'
```
```text
37cd922e0cfd58e99920e1d743852813a3b5636519e04d4ae74d0a5e03682efb  /dev/block/by-name/vendor_boot
```
This hash establishes byte identity of **currently installed** vendor_boot and is **not independently verified** against exact OEM A146PXXUHEZB1 AP firmware. Current running kernel remains Physwizz, custom patched 6.6.89.

Prior header-read from same partition:
```text
56 4e 44 52 42 4f 4f 54 04 00 00 00 00 10 00 00 00 00 08 40
```
Decodes vendor_boot v4, 4096-byte pages, kernel_addr `0x40080000`, and 512-KiB alignment yields DRAM offset `0x40000000`; physical RAM base also corroborated by current `/proc/iomem`.
Separate original OEM boot-only heuristic `0x80000000` conflicts; use header-derived candidate while not claiming original OEM validation.

## Explicit KernelSU Next integration blocker

[GhostLock app Kotlin source](https://github.com/YuKongA/ghostlock-app/blob/main/app/src/main/kotlin/com/ghostlock/app/data/AndroidGhostlockRepository.kt), function `prepareKsud()`, only searches packages `me.weishu.kernelsu.pr`, `me.weishu.kernelsu`, `com.resukisu.resukisu`, `org.bakasu.bakasu`, `com.kowx712.supermanager`. **KernelSU Next manager package `com.rifsxd.ksunext` is not among them**. The [native handoff script](https://github.com/YuKongA/ghostlock-app/blob/main/src/core/attack/ops.cpp) falls back to `/data/local/tmp/ksud` or `/data/adb/ksu/bin/ksud` on rooted systems, but this is not a verified clean stock/locked path and cannot be assumed after relocking/wipe.

[GhostLock handoff](https://github.com/YuKongA/ghostlock-app/blob/main/src/core/attack/ops.cpp) invokes `ksud late-load --kmi android15-6.6 --allow-shell`; watches for `kernelsu` in `/proc/modules` and requires module insertion.

[Pinned KernelSU Next source](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/userspace/ksud/src/late_load.rs) proves `ksud late-load` looks up **`android15-6.6_kernelsu.ko` in embedded ksud assets**, and then invokes `ksuinit::load_module`. A stock-compatible module alone is not enough: the `ksud` binary available to the GhostLock process must contain the **matching** LKM, and manager package discovery must be corrected / tested.

## Stock research compiler milestone and new CI job

CI [run 38827404310](https://github.com/wiredroid/Patch-Recovery/actions/runs/38827404310), job 116737971560 log line 476: `VMLINUX_COMPILE_EXIT=0` on partial official-GKI89 + partial Samsung delta source tree. This is a successful **research vmlinux compilation** with BTF analysis, not an OEM-equivalent binary. Prior Samsung 50→89 forward port leaves **44 unresolved vendor conflict paths**; source, symbol CRCs, module signing and ABI remain insufficiently demonstrated.

Workflow [`a146p-stock-6.6.89-abi-build.yml`](https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/.github/workflows/a146p-stock-6.6.89-abi-build.yml), commit `c2563bdee5518fb0135c56fba869fa00eaa3fee4`, now includes a **diagnostics-only KernelSU Next .ko compile step** after successful vmlinux, pinned to `159bc7da4266fd9331f63e25901629db4b7bfff8`, recording vermagic, module imports and modpost warnings. It may publish a binary only marked `UNVERIFIED-DO-NOT-LOAD`. **Never insert onto OEM stock just because CI succeeded**.

## Practical next safety gates

1. Obtain exact original `vendor_boot.img` from A146PXXUHEZB1 Samsung AP firmware to compare full SHA256 to live `37cd922e...`; if mismatch, re-evaluate origin.
2. Examine CI module results; validate against original OEM stock BTF, exact symbol CRCs and vendor policies, no fallback to the current Physwizz module.
3. Integrate `com.rifsxd.ksunext` manager `libksud.so` discovery into a GhostLock fork and bundle vetted OEM-compatible LKM in the correct `ksud` assets. Existing unverified GhostLock profile remains unregistered. Test only in a recoverable environment.
4. Original OEM boot/init_boot remain byte-for-byte; **do not re-lock bootloader with patched images**. Locked bootloader is never demonstrated by PIF fake props or static GhostLock reports.

Original stock boot SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`; original stock init_boot SHA256 `a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976`.
