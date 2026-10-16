# GhostLock A146P HEZB1 extracted profile vs original OEM BTF — 2026-10-17

**Status: UNVERIFIED research candidate; NOT a validated/registered kernel profile. No GhostLock execution has occurred. Do not run/flash/relock.**

Sources:
- Genuine Samsung A146PXXUHEZB1 OEM boot.img SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`.
- `ghostlock-extract-android-arm64` `--analysis` and `--format conf` outputs supplied by device owner after SHA256 validation, stock kernel `6.6.89-android15-8-abA146PXXUHEZB1-4k`.
- Independently exported real OEM BTF, SHA256 `169aa6aac6c8ff3d78bbda9d1b0942da12c84c2f491fdcbb504c36260090f67e`, archived in user-supplied `A146P_stock_6.6.89_BTF_and_decompilation_toolkit.zip`, `stock_btf/btf_struct_members.tsv`.
- Official GhostLock [schema](https://github.com/YuKongA/ghostlock-app/blob/main/docs/kernel_profiles/PROFILE_SCHEMA.md), [6.x credential defaults](https://github.com/YuKongA/ghostlock-app/blob/main/app/src/main/assets/kernel_profiles/credential-6x.conf), [KernelSnitch 6.x defaults](https://github.com/YuKongA/ghostlock-app/blob/main/app/src/main/assets/kernel_profiles/kernelsnitch-6x.conf) and [MediaTek instructions](https://github.com/YuKongA/ghostlock-app/blob/main/docs/kernel_profiles/MEDIATEK.md).

## Extracted candidate

Stored **outside** app's runtime asset directory, intentionally not registered: [`candidates/A146PXXUHEZB1-UNVERIFIED.conf`](candidates/A146PXXUHEZB1-UNVERIFIED.conf).

The genuine OEM `remove_waiter` is reported unpatched at image relative `0x10200f4`. Extractor selected `select_stack` (`waiter_shift=-2`, derived from OEM image). Static supported-family analysis is NOT a successful privilege escalation.

## 15/15 task_struct member offsets independently confirmed against OEM BTF (type ID 316)

| Field | Extracted & OEM BTF byte offset |
|---|---:|
| prio | 116 |
| normal_prio | 124 |
| sched_task_group | 840 |
| pi_lock | 2316 |
| pi_waiters | 2336 |
| pi_top_task | 2352 |
| pi_blocked_on | 2360 |
| pid | 1560 |
| tgid | 1564 |
| atomic_flags | 1496 |
| real_cred | 2072 |
| cred | 2080 |
| comm | 2096 |
| tasks | 1360 |
| seccomp | 2280 |

Note: `prio=116` is genuine Samsung stock BTF, not a typo for other 6.6.89 phones' 132. `task_struct` is 4800 bytes.

## Credential BTF cross-check

OEM `cred` BTF type ID 501: `usage=0`; `cap_inheritable=48`; `cap_permitted=56`; `cap_effective=64`; `cap_bset=72`; `cap_ambient=80`. Candidate `caps_offset=48`, count=5, size=136, consistent with that layout (whole `cred` struct is 184 bytes). Existing upstream 6.x `cred.usage_offset=null`, `ref_count=null`, `refN_*=null` are *the same intentional placeholders* as the shipped 6.x template, not necessarily execution blockers for select_stack.

The real OEM `rt_mutex_waiter` BTF type ID 16545 contains `tree=0`, `pi_tree=40`, `task=80`, `lock=88`, `wake_state=96`, `ww_ctx=104` (112 bytes): matches preflight report `0x0,0x28,0x50,0x58,0x60,0x68`. OEM `mm_struct` is 1216 = `0x4c0` bytes; `kernelsnitch.mm_struct_sz=null` follows upstream 6.6 select_stack defaults, which only require it for multicast route.

## Unresolved / boundaries

1. `kernel_phys_load=0x80000000` was **derived by static extractor** from OEM MTK compressed image; separate `kernel_phys_offset=null` is **not** resolved by that inference. MediaTek docs require correct distinct load / DRAM map addresses on actual device; do not assume both equal or copy neighbouring devices.
2. `warning: loggers_0_1 derivation failed: nfnetlink_log_init x1 does not materialize nfulnl_logger` despite the candidate `slide_loggers_0_1=31334832`; static source/assembly validation is advisable. Candidates' non-null slide numbers are not live-device proof.
3. Samsung DEFEX, KDP, RKP, SELinux, vendor LSM, KMI/vermagic/module signature and `ksud` handoff on *genuine signed, unmodified kernel* remain untested. A stock-compatible KSU Next `.ko` is still required.
4. Current device is unlocked + rooted on **Physwizz 6.6.89**, not original OEM. Do not use its running kernel as proof of original OEM live offsets or GhostLock reliability. Developer explicitly warns that a KSU-patched kernel interferes with physical-address extractor.
5. The built-in GhostLock supported-devices registry does not contain A146P exact `uname -r`; profile is not yet device-verified. Zero successful locked-bootloader root attempts have been demonstrated.

## Low-risk next measurement

On the currently rooted device, examine *read-only* `/proc/iomem` just for publicly interpretable DRAM-base layout **with explicit caution that current running kernel is Physwizz and not OEM**. A more reliable independent route is matching *original OEM* vendor_boot image where extractor can infer load/offset, followed by verification on physically original signed firmware; no exploit while running patched kernel. Do not bypass the developer's separate MediaTek gate.
