# Samsung A146P HEZB1: KernelSU Next vs BK-KSU Samsung compatibility and Strong Integrity
**18 Oct 2026 — static, read-only research. No live locked-kernel insertion or integrity spoofing.**

## Direct answer

**KernelSU Next v3.4.2 ALREADY implements Samsung-specific RKP, KDP, DEFEX and no-live-patch-text compatibility**, at pinned commit `159bc7da4266fd9331f63e25901629db4b7bfff8`. This implementation does not assert or guarantee hardware-backed **Google Play Integrity MEETS_STRONG_INTEGRITY** or restore the Knox warranty bit.

Samsung Real-time Kernel Protection (RKP) is a Samsung trusted kernel runtime security mechanism; Google's Play Integrity Strong verdict is a server-verified attestation assessment of an OEM-certified, locked device plus up-to-date system and vendor patch levels on Android 13+. **RKP feature-support code is not an attestation pass mechanism.**

## Pinned-source checks: KernelSU Next versus BK-KSU

| Feature | KernelSU Next v3.4.2 | BK-KSU v1.1.4 |
|---|---|---|
| Samsung `KSU_SAMSUNG_RKP` option | Present: `kernel/Kconfig` | No equivalent named option in `kernel/Kconfig` |
| Samsung `KSU_SAMSUNG_KDP` option | Present | No equivalent named option in `kernel/Kconfig` |
| Samsung `KSU_SAMSUNG_DEFEX` option | Present | No equivalent named option in `kernel/Kconfig` |
| Samsung `KSU_SAMSUNG_NO_PATCH_TEXT` option | Present | No equivalent named option in `kernel/Kconfig` |
| Samsung source-specific implementation | `kernel/compat/samsung_rkp.c`, `samsung_kdp.c`, `samsung_defex.c` | v1.1.4 source has generic hooks and patching, without comparable dedicated Samsung Kconfig implementation shown |
| `ksuinit` userspace load-module resolver | Exact same GitHub source blob SHA `1a62d4c2b18197d338451a4c809edd1308acc481` | Exact same SHA; no new `ksuinit` resolver logic to cherry-pick for this version |

BK release notes say “Samsung RKP/KDP/DEFEX compatibility framework” — **a product claim**, not proof that the ARM64 v1.1.4 module handles our exact Samsung firmware. BK binary `android15-6.6_kernelsu.ko` is built against 6.6.127, not A146P's 6.6.89 and had 64 OEM-unexported imported names versus our KSU Next build's 59 (see `A146P-BK-KSU-V114-STOCK-OEM-ABI-COMPARISON-2026-10-18.md`). This does **not** establish either module is safe to load into OEM.

## Our actual original Samsung A146P HEZB1 BTF proves WHY KDP stays off

Offline parser examined **61,049 BTF function declarations** from the owner's verified `boot.img` (SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`), not Physwizz's running kernel.

| Required function / prerequisite | OEM BTF result |
|---|---|
| `get_task_creds`, `set_task_creds`, `task_defex_enforce` (DEFEX) | All **present** |
| `register_kprobe`, `register_kretprobe` | Both **present** |
| `prepare_ro_creds`, `kdp_assign_pgd`, `kdp_usecount_dec_and_test` (KDP) | All **not declared** |
| `inc_rlimit_ucounts`, `dec_rlimit_ucounts` (other KDP dependencies) | Both **present** |

Exact stock IKCONFIG has `CONFIG_SECURITY_DEFEX=y`, `CONFIG_KPROBES=y`, `CONFIG_KRETPROBES=y`, `CONFIG_SECURITY_SELINUX=y`, `CONFIG_MODVERSIONS=y`, `CONFIG_MODULE_SIG_PROTECT=y`, `CONFIG_SAMSUNG_GKI_KERNEL=y`.

**Evidence-based experimental build flags already selected:**
- `CONFIG_KSU_SAMSUNG_RKP=y` — kprobe/kretprobe fallback available *at source/BTF prerequisite level*.
- `CONFIG_KSU_SAMSUNG_DEFEX=y` — stock BTF declares the 3 helper functions.
- `CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT=y` — avoid generic live fixmap/kernel-text modification on Samsung EL2.
- **`CONFIG_KSU_SAMSUNG_KDP=n` — correct for these BTF observations**. KSU Next `samsung_kdp.c` resolves the 3 missing helpers and fails init with `-ENOENT` when they aren't available. An unavailable BTF declaration is not conclusive absence from all execution contexts, but no evidence justifies enabling it.

`kernel/hook/syscall_hook_manager.c` calls `ksu_samsung_rkp_init` only if `ksu_dispatcher_nr < 0`; `samsung_rkp.c` registers kprobe syscall fallbacks plus setresuid kretprobe. **Compiling RKP enabled does not prove it was activated or that stock RKP allowed the hooks.** `kernel/compat/samsung_defex.c` resolves `get_task_creds` and `set_task_creds`, registers `task_defex_enforce` kprobe, and returns failure if helpers or hook registration fail. Their BTF presence is necessary evidence, not runtime execution proof.

## Google and Samsung hardware trust requirements are separate

- [Google's Play Integrity verdict documentation](https://developer.android.com/google/play/integrity/verdicts) specifies that **Android 13+ `MEETS_DEVICE_INTEGRITY` requires hardware-backed proof of locked bootloader and genuine certified OEM image**; `MEETS_STRONG_INTEGRITY` also requires system **and vendor** security updates within one year. Changing reported Android properties or RKP options does not replace that hardware proof.
- [Android's Key Attestation documentation](https://source.android.com/docs/security/features/keystore/attestation) defines hardware `RootOfTrust` values `deviceLocked`, `verifiedBootState` and `verifiedBootHash`.
- [Samsung Knox Warranty Bit documentation](https://docs.samsungknox.com/admin/fundamentals/kbas/kba-360039680233/) explains the irreversible one-time fuse when tripped by unofficial firmware; [Samsung's Knox FAQ](https://docs.samsungknox.com/admin/knox-platform-for-enterprise/faq/) says certain Knox capabilities can remain disabled thereafter. We **have not measured this owner's warranty bit**; do not assume its value.
- A factory Samsung signed OS with genuinely locked verified boot may meet Google's hardware-backed prerequisites, subject to certification, patch recency and clean runtime. **Root obtained later is not guaranteed to retain an approved verdict**, and should not be treated as a mechanism to fake it.
- Installing BK-KSU / KSU Next itself, altering boot, invoking RKP code or spoofing system properties does NOT prove or guarantee Strong Integrity, Knox/Samsung Pay/Secure Folder availability.

## Work remaining

1. Keep existing working Physwizz setup unmodified; do not flash generic BK module or relock with modified boot/init_boot.
2. Resolve the 59 KSU Next ELF imports not exported in the original OEM built-in `__ksymtab`; 160/160 exported CRC imports and `module_layout` already directly matched stock binary in `A146P-HEZB1-ORIGINAL-BOOT-KSYMTAB-160-CRC-EXACT-2026-10-18.md`.
3. Audit BK source changes *selectively*; current v1.1.4 `userspace/ksuinit/src/lib.rs` is **byte-for-byte identical Git blob** to KSU Next, so don't cherry-pick redundant loader code or generic live-patch features onto a protected Samsung kernel.
4. Validate RKP/DEFEX/loader use on genuine stock only through future separately assessed safe environment. Current evidence is static source/BTF and build diagnostics, **not a functional root or Strong Integrity result**.
5. If the user's top priority is authentic Strong Integrity and Samsung Knox features, assess official firmware/lock state, current system and vendor patches, and Knox fuse *before* considering any further flashing. No assurance rooted/modified device will be eligible.
