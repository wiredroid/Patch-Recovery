# A146P HEZB1 stock GhostLock static preflight — 2026-10-17

Status: **CVE-2026-43499 vulnerable-code pattern observed in original OEM boot image. This is NOT a working exploit, NOT a validated device profile, NOT a loaded stock KernelSU Next module, and NOT locked-bootloader root.**

## Provenance

- Samsung Galaxy A14 5G SM-A146P, firmware A146PXXUHEZB1, Android 15, shipping GKI 6.6.89.
- OEM **unmodified** `boot.img` SHA256: `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`.
- The owner independently extracted and SHA256-checked this image on-device: `A146PXXUHEZB1-original-boot.img: OK`.
- Analyzer: YuKongA/ghostlock-app official `ghostlock-extract-android-arm64` release pre-release, pinned SHA256 `3fc007a084b4f41bebf1e4190ac06edea06ffc44893694d5559f2af8571c5b60`. Invocation was **`--analysis` on OEM image**, never the kernel exploit.

## Exact static report supplied by device owner

```text
info: kallsyms layout 6.4+ recovered (117459 symbols)
info: (CVE-2026-43499 primitive present (remove_waiter@0x10200f4 still uses current)
info: MediaTek compressed image; _text confirms kernel_phys_load=0x80000000 (DRAM base)
== GhostLock kernel analysis ==
release                 6.6.89-android15-8-abA146PXXUHEZB1-4k
kernel_major            6.6
kernel_family           STRUCT_OFFSETS_6_6 (verified Android family)
kernel_phys_load        0x80000000 (MediaTek DRAM base)
rt_mutex_waiter         lock=0x58 pi_tree=0x28 task=0x50 tree=0x0 wake_state=0x60 ww_ctx=0x68 size=0x70
mm_struct size          0x4c0
primitive               remove_waiter@0x10200f4 unpatched
pselect chain           derived shift=-2 waiter=0x90 chain=__arm64_sys_pselect6->core_sys_select
path multicast_waiter   available (ip_mc_msfadd=absent ip_mc_source@0xffffffc080eb4920)
path select_stack       available (core_sys_select@0xffffffc0803c59a8 futex_wait@0xffffffc080196bb0)
path tcp_zerocopy       available (tcp_zerocopy_receive@0xffffffc080e765a4)
---------------------------------
suggested route         select_stack (high)
reasons                 - pselect/futex waiter layout derived from the kernel
note                    a device gate with the fixed CPU pair still decides whether a route is supported
```

## Interpretation and constraints

1. This is stronger evidence than broad kernel family compatibility: **the real A146P OEM image has the unpatched `remove_waiter` pattern**. This is still a static check and **does not verify successful privilege escalation or module loading**.
2. The reporter is running rooted Physwizz 6.6.89 + KSU Next on an **unlocked** device; it is not a valid live stand-in for the original signed Samsung kernel. Never use live `/proc/kallsyms` as OEM offsets if it refers to Physwizz.
3. Developer's [MediaTek instructions](https://github.com/YuKongA/ghostlock-app/blob/main/docs/kernel_profiles/MEDIATEK.md) require correctly determined physical load and physical offset; `kernel_phys_load=0x80000000` is the extractor's static inference, **not** proof that the other MediaTek physical address, `kernel_phys_offset`, is correct. Their helper explicitly rejects KernelSU-patched kernels and requires separate device validation.
4. A146P's release `6.6.89-android15-8-abA146PXXUHEZB1-4k` does not appear in the GhostLock app's pre-bundled exact-match supported profiles, even though multiple other unrelated `6.6.89` kernels are listed. Do not import neighbour-device offsets.
5. Samsung KDP, RKP, DEFEX, SELinux, loadable module permission/signature, KernelSU Next matching `.ko`, reboot-persistence and actual bootloader state all remain separate, **unverified** hurdles.

## Next static milestone

Use the same pinned ARM64 analyzer against verified OEM `boot.img` with `--format conf --out <candidate>.conf` to obtain its image-specific source profile. Compare required fields against the [GhostLock profile schema](https://github.com/YuKongA/ghostlock-app/blob/main/docs/kernel_profiles/PROFILE_SCHEMA.md). File stays **UNVERIFIED / DO NOT EXECUTE** until all required values and real-device validation exist. Never relock or flash experimental images.
