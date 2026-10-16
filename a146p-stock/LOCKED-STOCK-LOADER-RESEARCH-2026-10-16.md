# Genuine A146P HEZB1 locked-bootloader root research — 2026-10-16

**Status: NO VERIFIED A146P LOCKED-BOOTLOADER ROOT OR STOCK MODULE LOADER.**
Target: Samsung Galaxy A14 5G SM-A146P (MT6833), original OEM-signed firmware `A146PXXUHEZB1`, Android 15, Linux `6.6.89-android15-8-abA146PXXUHEZB1-4k`. This note is research-only, not an exploit or flashing procedure.

## Core feasibility gate

Keeping `boot.img` and `init_boot.img` byte-for-byte original is mandatory for the genuine OEM-verified locked boot flow:
- SHA256 original boot: `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`.
- SHA256 original init_boot: `a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976`.

Both originals were located in the user Files Library and hashes verified. A source-rebuilt kernel or modified init ramdisk cannot retain those OEM byte hashes. A KernelSU Next LKM compatible with the stock ABI still cannot load itself: each reboot needs an independently demonstrated privilege path, compatible and permitted module insertion, correct imports/CRCs/vermagic, signature policy satisfaction, and interaction tests with DEFEX, SELinux and vendor protections. Prior FolkPatch privileges do not survive a reboot into original OEM stock boot.

## Current kernel CVE research; DO NOT cross-apply device profiles

- `CVE-2026-43499` (GhostLock) **is real and has public independent research** for a *different* Samsung model: the Samsung Galaxy A17 SM-A175F, with MT6789, **Linux 6.12 / Android 16**; see https://github.com/mobilehackinglab/ghostlock-a17 and https://www.mobilehackinglab.com/blog/cve-2026-43499-ghostlock-a17-root-shell . That does **not** establish the SM-A146P 6.6.89 is vulnerable, has the required memory-layout primitives, or can persistently load a module.
- Public kernel-specific GhostLock profile lists (e.g. https://github.com/YuKongA/ghostlock-app/blob/main/docs/kernel_profiles/SUPPORTED_DEVICES.md) include some **non-Samsung** Android15 6.6.89 phones, but this does **not** authorize reusing offsets or exploit configuration from another kernel. Search completed 2026-10-16 found no verified `A146PXXUHEZB1` profile or A146P live exploit.
- Samsung-specific safeguards need independent tests and successful proof, particularly Samsung kernel data protection (where applicable), DEFEX restrictions, SELinux, lockdown/module policy and signed module handling. An unverified extracted offset profile, a tool saying 'supported kernel 6.6.89', or a test on A17 is not proof on A146P.

## US MediaTek cousin and genuine GPL source

Samsung's official US SM-A146U update page documents Android15 `A146USQSJEZH3` on 2026-08-26: https://doc.samsungmobile.com/SM-A146U/025654230214/eng.html. SamMobile lists US `A146USQSJEZH3` and Australian `A146PXXUHEZB1` with the same reported changelist `31154426` (https://www.sammobile.com/samsung/galaxy-a14-5g/firmware/SM-A146U/TMK/download/A146USQSJEZH3/2018989/ and https://www.sammobile.com/samsung/galaxy-a14-5g/firmware/SM-A146P/VAU/download/A146PXXUHEZB1/2019634/). **This is NOT proof of identical kernel source, kernel version, ABI or module CRCs**: US and Australian releases, build timestamps and software revisions differ. The Samsung official A14 open-source listing https://opensource.samsung.com/uploadSearch?searchValue=A14 confirms A146P Android15 GPL and A146B Android15 archives, but no official A146U/A146U1 Android15 GPL source ZIP was verified in this audit. Request an exact A146P HEZB1 6.6.89 GPL release and Module.symvers, and specific US variant archives, from https://opensource.samsung.com/requestInquiry .

## Practical next gates

1. Finish compiling an independent Samsung-ported GKI89 candidate, then compare **all relevant stock BTF members, symbol CRCs and security config** to original `boot.img`; reserve the label experimental until proven on actual kernel.
2. Separately establish a safe, privilege-independent kernel module loader on the *exact original stock* HEZB1 kernel, while maintaining OEM-signed images and bootloader state. No such verified method currently exists.
3. Any unlocked Physwizz → KernelSU Next boot-persistent migration must stay a separate rollback-capable project. Do not relock, flash untested kernels or assume APatch→stock preserves root.

**No locked-bootloader flashing or exploit instructions are recommended by this note.**

## 2026-10-16 follow-up: Samsung's October GhostLock security patch & Strong Integrity

**Verified new official evidence:** Samsung's October 2026 Security Maintenance Release
(https://security.samsungmobile.com/securityUpdate.smsb?month=10&year=2026)
explicitly lists \`CVE-2026-43499\` in its **Google High CVE** section, among patches included in its October maintenance package. The bulletin notes that rollouts can vary by model/region and some chipset-specific patches may be delayed. This **does not** prove SM-A146P specifically was previously vulnerable, nor prove that the user's \`A146PXXUHEZB1\` image includes or lacks the fix. Treat its reported 2026-10-05 security patch date as a reason to inspect exact build/vendor code before any GhostLock feasibility assertion, not evidence of exploitability.

The independently tested Samsung GhostLock port (https://github.com/mobilehackinglab/ghostlock-a17) is for A17 MT6789 Android16 Linux6.12 on different bootloader/security conditions; its offsets and primitive chain cannot safely be transferred to SM-A146P MT6833 Android15 Linux6.6.89. This is an **unverified locked-stock loader hypothesis**, not a working device-root mechanism.

**Google Play Integrity:** The API's \`MEETS_STRONG_INTEGRITY\` label still exists (https://developer.android.com/google/play/integrity/verdicts). Since May 2025, Android 13+ verdicts require stronger hardware-backed security signals; Strong also requires recent system and vendor security patches. New community discussion on 2026-10-14/15 reports revoked public keyboxes and vanished integrity for some rooted phones (https://www.reddit.com/r/Magisk/comments/1x5zoob/how_to_fix_this_error/). Those are **reports**, not official proof that Google retired the Strong tier, nor evidence a spoofed locked state becomes genuine verified boot.

**Physical bootloader status remains unlocked** for the currently functioning Physwizz+KernelSU Next boot chain. Never relock it with custom \`boot\`/\`init_boot\`; original OEM-signed images' SHA256 identity is mandatory for the true stock research target. The stock source compiler run \`38807656141\` failed on \`f2fs_has_compressed_data\` undeclared in \`fs/f2fs/extent_cache.c\`; the previously prepared focused Samsung F2FS patch \`0004\` is now wired into the stock branch workflow commit \`b4e9a97d643f3b7137f07f9feb7772a9bd66f891\` and checked by CI run https://github.com/wiredroid/Patch-Recovery/actions/runs/38827404310. A new compile advancing past this error **will not constitute stock ABI match or proof of locked-BL root**.
