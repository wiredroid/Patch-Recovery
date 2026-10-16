# A146P HEZB1 GhostLock ⇢ KernelSU Next ksud handoff progress, 17 Oct 2026

**Only build/static tests have run. No stock exploit, module insertion, custom phone flashes or bootloader lock changes.** The user currently runs Physwizz 6.6.89 + KernelSU Next and must not use the Samsung stock-offset GhostLock profile on Physwizz.

## Completed: source-level integration check

- Existing pinned [GhostLock integration Kotlin CI #38960339994](https://github.com/wiredroid/Patch-Recovery/actions/runs/38960339994) completed successfully.
- Kotlin patch `patches/0001-ghostlock-prepareksud-detect-ksunext-manager.patch` adds `com.rifsxd.ksunext` to package visibility and `prepareKsud()` lookup of `libksud.so`.
- New native patch `patches/0002-ghostlock-native-ksunext-ksud-fallback.patch` covers `src/core/attack/ops.cpp` shell fallback `/data/app/*/com.rifsxd.ksunext*/lib/arm64/libksud.so`; protects against Kotlin copy path being unavailable. Both patches are applied by the CI workflows on pinned official GhostLock `847793ea7f936c241f38f2ca840d382162ac5256`.
- New read-only [ksud source/ELF handoff audit #38962663941](https://github.com/wiredroid/Patch-Recovery/actions/runs/38962663941) **PASSED**. It verifies AndroidManifest/Kotlin/native discovery, upstream `late-load` CLI contract, `android15-6.6_kernelsu.ko` RustEmbed filename and experimental .ko SHA256 `3ed5fda0fd042af69f778876f223d3d803ae27042bcf3101d37d48cb5345ec0e`. This test does NOT compile or verify a manager APK or binary ksud package.

## Exact pinned KernelSU Next behavior (v3.4.2, 159bc7da4266fd9331f63e25901629db4b7bfff8)

- `userspace/ksud/src/cli.rs`: `late-load --kmi android15-6.6 --allow-shell` is recognized; `--package-name` defaults to `com.rifsxd.ksunext`.
- `userspace/ksud/src/late_load.rs`: resolves `format!("{kmi}_kernelsu.ko")` and retrieves it with `assets::get_asset_data` using `RustEmbed`. Then passes module to `ksuinit::load_module`.
- `userspace/ksud/src/assets.rs`: Android AArch64 `Asset` derives `RustEmbed` from `userspace/ksud/bin/aarch64`. Therefore an exact stock-compatible .ko must be staged as `userspace/ksud/bin/aarch64/android15-6.6_kernelsu.ko` **before building ksud**; adding a standalone module file to a running phone or installing standard manager doesn't establish this.
- `userspace/ksuinit/src/lib.rs`: tries `/proc/kallsyms` symbol relocation, calls `init_module`, and can retry a vermagic mismatch. Neither substitution nor runtime relocation means exact Samsung ABI compatibility or permission is proven.
- GhostLock C++ `write_root_script()` invokes `"$KSUD" late-load --kmi "$KMI" --allow-shell`, then polls `/proc/modules` for `kernelsu`. If original GhostLock privilege escalation hasn't succeeded, ksud cannot skip that stage.

## New experimental Android ksud compilation experiment

[`a146p-ksud-android-embed-preflight.yml`](../../.github/workflows/a146p-ksud-android-embed-preflight.yml) downloads the exact checksum-pinned experimental KernelSU Next .ko from corrected GKI89 build #38942607886, copies it into the pinned KSU source's expected AArch64 KMI asset path, and attempts to compile **Android ARM64 `ksud`** with NDK+Rust. It records ELF header and hashes but **intentionally never uploads a runnable ksud, .ko or APK**. It is a provenance and packaging build study only, not a stock-loader validation. [First build run #38962895723](https://github.com/wiredroid/Patch-Recovery/actions/runs/38962895723).

## Remaining non-negotiable technical gates

1. The compiled research `kernelsu.ko` uses `6.6.89-4k-gebbf6177d5ae-dirty` **not** the exact OEM `6.6.89-android15-8-abA146PXXUHEZB1-4k` vermagic. A loader workaround does NOT fix ABI divergence.
2. 59 of 219 undefined imports are not exported by the partial reconstructed GKI89 kernel. Original OEM BTF identifies names of 53 as functions and leaves six data/tracepoint references without BTF FUNC evidence, but actual OEM symbols, CRCs, namespace and load permissions have not been established.
3. Original Samsung `Module.symvers` export CRCs are unavailable, while `CONFIG_MODVERSIONS=y`, `CONFIG_MODULE_SIG_PROTECT=y` and `CONFIG_SECURITY_DEFEX=y` are active. Samsung/MTK production signing key is unavailable; dev key is untrusted.
4. The original signed OEM kernel has an unpatched CVE-2026-43499 code pattern in static analysis, but W1-W3 exploit success on a real signed, factory-locked A146P was never demonstrated. Physical address inference and profile are research candidates.
5. Even a successfully compiled Android `ksud` cannot be assumed included in an installed KernelSU Next manager's `libksud.so`, or load the experimental .ko successfully. A matching Android APK, module and loader need the full verified OEM compatibility gate.

**No claim of root on a factory-locked A146P. Do not load this research LKM or relock with modified boot/init_boot.**
