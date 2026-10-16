# A146P HEZB1 — Android GKI unsigned-module policy vs KernelSU Next late loading
**2026-10-17. Read-only source audit; DO NOT LOAD the experimental LKM on OEM kernel.**

## Exact stock configuration (extracted from ORIGINAL OEM boot)
```config
CONFIG_MODULES=y
CONFIG_MODVERSIONS=y
CONFIG_MODULE_SIG=y
# CONFIG_MODULE_SIG_FORCE is not set
CONFIG_MODULE_SIG_PROTECT=y
CONFIG_MODULE_SIG_ALL=y
CONFIG_MODULE_SIG_KEY="$(DEVICE_MODULES_REL_DIR)/certs/mtk_signing_key.pem"
CONFIG_SECURITY_DEFEX=y
CONFIG_SAMSUNG_GKI_KERNEL=y
```

Do not mistakenly equate `MODULE_SIG_PROTECT` with `MODULE_SIG_FORCE`. They have substantially different semantics. The actual OEM policy must still be verified, including vendor SELinux, DEFEX and Samsung security features.

## Source evidence on matching kernel family (Physwizz A146P 6.6.89; not claimed exact OEM)

Samsung-derived Android GKI 6.6 `kernel/module/signing.c`:
https://github.com/physwizz/a146p/blob/6560c1ca1f009dd3e53b698245bf2df1b9804e03/kernel-6.6/kernel/module/signing.c

When not enforcing `MODULE_SIG_FORCE`, unsigned modules can pass `module_sig_check` with `MODULE_SIG_PROTECT`: `#ifdef CONFIG_MODULE_SIG_PROTECT` branch returns 0 for otherwise unmodified unsigned modules. However **protection against using privileged GKI exports is checked separately**.

Samsung-derived GKI `kernel/module/main.c`:
https://github.com/physwizz/a146p/blob/6560c1ca1f009dd3e53b698245bf2df1b9804e03/kernel-6.6/kernel/module/main.c

`resolve_symbol` verifies imported export CRCs, namespace, and then (for an unsigned vendor module) `gki_is_module_unprotected_symbol(name)`. Protected exports can be rejected with `-EACCES`. `kernel/module/Kconfig` explicitly describes GKI unprotected/vendor imports and the permission-denied behavior:
https://github.com/physwizz/a146p/blob/6560c1ca1f009dd3e53b698245bf2df1b9804e03/kernel-6.6/kernel/module/Kconfig

This is **not proof** OEM Samsung HEZB1 has the same implementation or same protected-symbol list as Physwizz. OEM config enables the feature, but executable enforcement depends on OEM build and other policies.

## KernelSU Next's actual loader strategy (pinned v3.4.2 code)

`ksud late-load` in
https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/userspace/ksud/src/late_load.rs

- Selects embedded `{kmi}_kernelsu.ko` asset, including `android15-6.6_kernelsu.ko` with `--kmi android15-6.6`;
- Delegates to `ksuinit::load_module`:
https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/userspace/ksuinit/src/lib.rs
- This loader tries to match undefined ELF imports against real `/proc/kallsyms`, replacing found imports with absolute-address references (`SHN_ABS`) in an **in-memory ELF copy** before `init_module`. It requires permission to read valid (nonzero) kernel symbol addresses and write `kptr_restrict`, which the physical rooted Physwizz device is not proof for original stock after GhostLock.
- On certain kernel log-identified failures it can rewrite `vermagic` in the in-memory ELF and retry. This is an engineering compatibility provision, **NOT ABI validation**.
- A stock-compatible `.ko` must be embedded within the `ksud` manager's `libksud.so`; copying a standalone experimental `.ko` onto a locked-stock phone will not make GhostLock handoff work.

## What is established / what still blocks

- Current corrected experimental `.ko` compilation succeeded on a partial GKI89 reconstruction, SHA256 `3ed5fda0fd042af69f778876f223d3d803ae27042bcf3101d37d48cb5345ec0e`.
- 59 direct imports absent from reconstructed export list, many function names present in OEM BTF. Their runtime availability and usability are **unconfirmed**.
- `MODULE_SIG_PROTECT` does not imply outright unsigned-module rejection under this *reference implementation*. GKI unprotected-list and namespace policies remain important. Source-matched unsigned loading is conceivable, not established.
- Actual original Samsung `Module.symvers` CRCs, the six data/tracepoint imports, **all** native module ABI, Samsung DEFEX/RKP/KDP, exact original stock GhostLock W1-W3 reliability, and `ksud` manager embedding must be validated.
- No stock root success, no live LKM load, no locked bootloader test. Do not flash stock boot over current functioning Physwizz/KernelSU Next or relock.

Research source is for analysis only and deliberately includes no exploit execution commands, module insertion, or module-signature bypass steps.
