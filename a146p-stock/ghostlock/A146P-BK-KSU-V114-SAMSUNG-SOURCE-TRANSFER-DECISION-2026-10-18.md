# BK-KSU v1.1.4 Samsung-support transfer decision for Galaxy A14 5G HEZB1

Date: 18 October 2026. **Pinned-source and original OEM-BTF audit only. No kernel module loaded or exploit executed.**

## Acknowledge the release claim

[BK-KSU 1.1.4](https://github.com/bklynali/BK-KSU/releases/tag/v1.1.4) explicitly announces “Samsung RKP/KDP/DEFEX compatibility framework,” plus recovery-APK LKM installation, module install-time risk detection, LMK SUSFS and dynamic RAM spoofing. These are legitimate release claims. They are not, alone, proof of **factory-locked, Samsung-signed, unchanged** boot compatibility on this precise **MediaTek SM-A146P, A146PXXUHEZB1, stock Linux 6.6.89**.

The same release also warns **“Do not update if you are using GKI.”** Our handset uses GKI android15-6.6. Recovery APK flashing and the `boot-patch-v2` utility do not preserve the unchanged signed boot partition demanded by this project.

## Critical pinned-source finding

The complete `userspace/ksuinit/src/lib.rs` is **byte-for-byte identical** between the BK v1.1.4 tag and our pinned KernelSU Next 3.4.2 source: Git blob SHA **`1a62d4c2b18197d338451a4c809edd1308acc481`**. Thus their `/proc/kallsyms` symbol enumerator, ELF relocation of unresolved imports, `init_module` syscall and vermagic retry are identical. **There is no newly improved BK-KSU symbol resolver to cherry-pick** for the 59 remaining imports in the current A146P candidate.

The v1.1.4 BK kernel [`kernel/Kconfig`](https://github.com/bklynali/BK-KSU/blob/v1.1.4/kernel/Kconfig) has no dedicated `KSU_SAMSUNG_RKP`, `KSU_SAMSUNG_KDP`, `KSU_SAMSUNG_DEFEX`, or `KSU_SAMSUNG_NO_PATCH_TEXT` config toggles. Its generic [ARM64 syscall hook](https://github.com/bklynali/BK-KSU/blob/v1.1.4/kernel/hook/arm64/syscall_hook.c) calls live `ksu_patch_text()` on a `sys_call_table` slot, and its [patch helper](https://github.com/bklynali/BK-KSU/blob/v1.1.4/kernel/hook/arm64/patch_memory.c) uses `set_fixmap_offset` and `stop_machine`. Those approaches could conflict with protected Samsung EL2 memory; the original A146P OEM runtime has not verified their permissibility. This audit of named source files does not categorically disprove the release's broad Samsung-support claims or its compatibility on other devices.

By contrast, our pinned KSU Next [Samsung Kconfig](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/Kconfig) and [Kbuild](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/Kbuild) provide specific external-module `ccflags-y` defines and source implementations:
- [`samsung_rkp.c`](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/compat/samsung_rkp.c): kprobe/kretprobe syscall fallback instead of depending solely on a writable syscall table.
- [`samsung_defex.c`](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/compat/samsung_defex.c): DEFEX task credential integration.
- [`samsung_kdp.c`](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/compat/samsung_kdp.c): optional KDP credential path.
- [`kernel/hook/arm64/patch_memory.c`](https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/hook/arm64/patch_memory.c): the `CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT` branch returns `-EOPNOTSUPP`, disabling unsafe live writes.

Our [HEZB1 research kernel build](https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/.github/workflows/a146p-stock-6.6.89-abi-build.yml) explicitly passes `CONFIG_KSU_SAMSUNG_RKP=y CONFIG_KSU_SAMSUNG_DEFEX=y CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT=y CONFIG_KSU_SAMSUNG_KDP=n`. CI now checks the corresponding `ccflags-y += -DCONFIG_...` definitions really exist in the pinned Kbuild, not merely Kconfig names.

## Exact original Samsung boot BTF checks

Original Samsung `boot.img` SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`, embedded BTF SHA256 `169aa6aac6c8ff3d78bbda9d1b0942da12c84c2f491fdcbb504c36260090f67e`. Independently parsed from 61,049 BTF function prototypes:

| Kernel function | OEM BTF FUNC evidence |
|---|---|
| `get_task_creds` | present; signature matches KSU Next DEFEX helper |
| `set_task_creds` | present; signature matches KSU Next DEFEX helper |
| `task_defex_enforce` | present |
| `prepare_ro_creds` | not declared |
| `kdp_assign_pgd` | not declared |
| `kdp_usecount_dec_and_test` | not declared |

BTF absence alone does not disprove a function's existence; actual execution/exports remain unverified. Exact stock config has `CONFIG_SECURITY_DEFEX=y`, `CONFIG_KPROBES=y`, `CONFIG_KRETPROBES=y`, `CONFIG_MODULE_SIG_PROTECT=y`, `CONFIG_MODVERSIONS=y`. Do not enable KDP gratuitously.

## Binary result and planned transfer

Earlier [BK-KSU A146P binary CI #39049794291](https://github.com/wiredroid/Patch-Recovery/actions/runs/39049794291) established BK v1.1.4 generic `android15-6.6_kernelsu.ko` has **254 imported ELF symbols**, of which **64** are not in the original OEM built-in export table. Our pinned A146P KSU Next experimental module has **219 imports**, **59** not exported; original `boot.img` matches **160/160** versioned imported symbols plus `module_layout`, while BK's generic release `.ko` lacks recoverable module CRC version entries in our ELF parser and carries non-OEM `6.6.127` vermagic. Neither may be loaded on stock.

**Transfer decision:** no unvalidated BK kernel hook or generic binary is being merged into our A146P source; the BK loader is identical to the existing one. BK's user-facing module risk detection and memory features may be useful after root is solved, but do not address bootloader-locked LKM insertion. Preserve existing Samsung flags, the KSU Next module, and the unmodified original images.

## Reproducibility

- Pinned BK v1.1.4 commit: `25c8d24ea06f0f8e19eda4d761e98d3e8c417131`.
- Pinned KSU Next 3.4.2 commit: `159bc7da4266fd9331f63e25901629db4b7bfff8`.
- New checked-in OEM DEFEX/KDP metadata: `A146P-HEZB1-STOCK-DEFEX-KDP-BTF-EVIDENCE-2026-10-18.json`.
- New [static code-level audit](https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/tools/audit-bk-v114-samsung-compat.py) and GitHub Actions `.github/workflows/a146p-bk-samsung-source-hardening-audit.yml`, initially successful [run #39051657463](https://github.com/wiredroid/Patch-Recovery/actions/runs/39051657463). Subsequent source-parity and Kbuild preprocessor checks are being rerun by CI.

**No claim of root on locked stock Samsung, no GhostLock exploit validation, and no proof that a production OEM kernel will accept the module.**
