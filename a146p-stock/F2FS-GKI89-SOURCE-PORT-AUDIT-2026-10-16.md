# F2FS corruption-dump source repair — Samsung A146P GPL50 → GKI89

**Research-only checkpoint, 2026-10-16 (Sydney).** This is a source reconstruction hypothesis, **not** an independently verified Samsung A146PXXUHEZB1 stock kernel or a safe module/flash artifact.

## Reproduced failure
GitHub Actions [run 38769715340](https://github.com/wiredroid/Patch-Recovery/actions/runs/38769715340), job `116542025665`: Clang compilation stopped at `fs/f2fs/dir.c:1148:5` because `print_block_data` was undeclared. The conservative 343-file source forward-port from Samsung GPL Linux 6.6.50 onto official GKI 6.6.89 left the newer GKI header in place while retaining Samsung's modified `dir.c` caller. The original 44 unresolved conflicts remain a **separate** backlog.

## Grounded source tracing
- Samsung A146P 6.6.50 public source mirror `joeyduzit/a146p_a14xm_stock_kernel`: `kernel-6.6/fs/f2fs/f2fs.h`, helper at ~3765; caller `kernel-6.6/fs/f2fs/dir.c` ~1124. (Mirror is not a fresh cryptographic check of the user's uploaded official GPL archive.)
- Pinned `physwizz/a146p` SHA `6560c1ca1f009dd3e53b698245bf2df1b9804e03`, `kernel-6.6/fs/f2fs/f2fs.h`, helper ~3818, caller ~1148: **implementation matches the A146P 6.6.50 mirror exactly**. Physwizz remains comparison-only, not the source for the independent stock target.
- Pinned `physwizz/A145r` SHA `652449d2c4e9e18ec41a3c4277ab8b2230534878`, same helper ~3818 and caller ~1148: **same helper bytes** as both A146P references. The A145R is not the same hardware.
- Pinned Galaxy A34 6.6.89 `Fede2782/kernel_samsung_mediatek_common` SHA `6dfa2540bbfd95ed6475933f4b6f925c6a644e6c`: no `print_block_data` in `fs/f2fs/f2fs.h` or `dir.c`.
- Official Android15 GKI89 commit `ebbf6177d5ae521e9902af2816ef56ff366bccfa`: no helper in `fs/f2fs/f2fs.h`; keeps its later F2FS core declarations/logic.

## Dependency and behavior
Samsung's helper accepts `struct f2fs_sb_info *`, a block number, the directory page data, start and length. On corrupt directory entries (`-EINVAL`) the caller emits diagnostic hex output, then invokes `f2fs_bug_on(sbi, 1)`. The helper uses `f2fs_err`, `struct mount`, ctype helpers, and the Samsung shutdown guard `ignore_fs_panic`.

The guard is **defined** in A146P50 and pinned Physwizz's `kernel-6.6/kernel/reboot.c` (same file blob SHA `a216f8971d23d1ff35821238d9b8de7597f55808`); it is assigned `1` before `device_shutdown()` in restart/halt handling. Official GKI89's `kernel/reboot.c` lacks the symbol. The candidate must demonstrate that the Samsung `reboot.c` delta survived and links; an extern alone is insufficient.

## Applied source overlay and CI
- [Source repair patch](patches/0001-f2fs-restore-samsung-corruption-dump-helper.patch) is a minimal diff over GKI89 `fs/f2fs/f2fs.h` that restores the **exact helper body** from the A146P50 reference; it adds only the required ctype/mount header dependencies and `ignore_fs_panic` declaration. No stubs, disabled warnings, bypassed checks, or Physwizz filesystem wholesale replacement.
- Isolated-branch patch commit `8d9f2d052301c600ad5cd60de2964e92869de591`.
- Workflow integration was corrected in commit `927391378c6fd7739e7e1c3ec14951b2fd5244d5` after an initial invalid-YAML text-edit attempt. The workflow uses `git apply --check`, records the resulting header diff and helper patch SHA-256, and inspects `ignore_fs_panic` C references.
- [Rebuild run 38778209850](https://github.com/wiredroid/Patch-Recovery/actions/runs/38778209850) is the source-application and kernel compile validation; inspect final result and diagnostics, not merely job launch.

## Independent stock compatibility gates still open
1. Full `vmlinux` link with stock-derived `olddefconfig`; `CONFIG_SAMSUNG_GKI_KERNEL=y` missing in earlier candidate. Stock config also has `CONFIG_TZDEV=m`; A146P50 mirror has no tzdev in expected `drivers/misc` or `drivers/tee` directories. Do **not** invent Kconfig settings to hide this drift.
2. Compare **full BTF member offsets, bitfield details, and prototypes** against real stock BTF (141,882 records), not only eight structure sizes.
3. Compare stock exports, kernel symbol presence, CONFIG_MODVERSIONS CRCs, exact vermagic, F2FS on-disk compatibility, SELinux/DEFEX behavior, module-signature enforcement and trusted keys. Research signing key is **not** Samsung's key.
4. No stock-compatible KernelSU Next `.ko`, safe stock module load, autonomous boot-persistent migration, or locked-bootloader root is demonstrated. Original OEM signed boot and init_boot must remain unmodified for locked-bootloader research; an independently verified privileged loader would still be required.

Do not flash these reconstructed or comparative-source kernel images.
