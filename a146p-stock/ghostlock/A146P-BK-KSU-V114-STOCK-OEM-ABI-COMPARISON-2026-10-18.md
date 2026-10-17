# BK-KSU v1.1.4 on original Samsung A146P HEZB1 6.6.89: offline compatibility assessment

Date: 18 Oct 2026. **Do not load, flash, or use this generic module on locked Samsung firmware.**

## Release facts
Official fork release [bklynali/BK-KSU v1.1.4](https://github.com/bklynali/BK-KSU/releases/tag/v1.1.4), published 2026-10-17T15:01:15Z, says “Samsung RKP/KDP/DEFEX compatibility framework”; the release description also explicitly says “Do not update if you are using GKI.” It provides `android15-6.6_kernelsu.ko` (466,480 bytes), manager APK, and Android arm64 `ksud` and `ksuinit`. **This is a release claim, not validation for SM-A146P HEZB1.**

## Reproduced checks
- [CI run #39049794291](https://github.com/wiredroid/Patch-Recovery/actions/runs/39049794291) fetched the v1.1.4 binary directly, checked 466,480-byte length, read ELF ARM64 imported symbols and modinfo, and compared it to our [pinned A146P reconstructed KSU Next build #38967262315](https://github.com/wiredroid/Patch-Recovery/actions/runs/38967262315). Report artifact #12106842500 holds module-import lists, CRC records and SHA256 hashes, **no runnable modules**.
- The released BK `.ko` has **254 undefined ELF imports**; 216 imported names overlap KSU Next, 38 are unique to BK and three are exclusive to our pinned KSU Next. The pinned KSU Next `.ko` has **219 imports**.
- Independent offline cross-join with the 16,238 exported-symbol names derived from the **actual original Samsung HEZB1 boot.img** (SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`):
  - BK: **190 of 254** names in Samsung original export table, **64 not exported**.
  - KSU Next: **160 of 219** names exported, **59 not exported** (existing OEM audit).
- BK release module's `vermagic`: **`6.6.127-4k-g46a034eca005-dirty SMP preempt mod_unload modversions aarch64`**, not `6.6.89-android15-8-abA146PXXUHEZB1-4k`.
- Our ELF parser recovered **zero readable `__versions` or extended-version CRC records** in BK release module; BK `module_layout` CRC therefore **unverifiable**, not known equal to OEM. This finding is for the unmodified downloaded binary and the currently implemented ELF formats; a different module loader may still resolve symbols dynamically. Our pinned rebuilt KSU Next .ko has **161 CRC records**, with **all 160 imported exported CRCs and module_layout** independently matched to the original Samsung Image.

## Source findings: Samsung compatibility is not a drop-in proof
- Pinned BK release kernel `kernel/Kconfig` has no explicit `CONFIG_KSU_SAMSUNG_RKP`, `CONFIG_KSU_SAMSUNG_DEFEX`, `CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT` options. By contrast, our KSU Next module CI passed explicit Samsung flags for reconstructed kernel; however these flags by themselves cannot prove runtime compatibility either.
- BK `userspace/ksud/src/late_load.rs` retrieves embedded `{kmi}_kernelsu.ko` and passes it to `ksuinit::load_module`. Similar in principle to our existing GhostLock handoff.
- BK `userspace/ksuinit/src/lib.rs` uses `/proc/kallsyms` to relocate missing symbols before `init_module`. This is **not a substitute for a privilege-escalation primitive or Samsung verification bypass**.
- BK `userspace/ksud/src/lkm_image.rs` exposes `boot-patch-v2`, a mechanism to **patch the boot image** via BTF/kallsyms and append a module payload. Patching a boot image changes its bytes and invalidates the original Samsung verified signature, so this is **not an OEM-signed factory-locked boot solution**. Do not attempt to flash it or relock.
- BK's `Magica` late-load flag is another way of arranging already privileged/ADB-root loader context; it does not by itself establish exploitable GhostLock on this handset.
- The release's blanket "Samsung RKP/KDP/DEFEX compatibility framework" has not been traced to a concrete, device-specific proof that our SM-A146P HEZB1 stock kernel will accept its module.

## Bottom line
BK-KSU 1.1.4 has potentially interesting loader and Samsung-hardening handling code **worth studying and adapting cautiously**, but its **off-the-shelf .ko is worse than the pinned A146P KSU Next experimental module on exact stock ABI evidence**, with five more nonexported imports and no verifiable module CRCs. Stick with the 160/160 OEM-CRC-matched experimental KSU Next research branch; focus on 59 nonexported imports, GhostLock success on the genuine stock kernel, Samsung runtime protection policy and trusted artifact packaging. No stock root proven.
