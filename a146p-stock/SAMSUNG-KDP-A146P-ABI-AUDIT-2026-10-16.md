# SM-A146P HEZB1 Samsung KDP compatibility audit (2026-10-16)

Research only; branch a146p-ksunext-stock-build. No boot images or partition writes.

## Findings

The Physwizz 6.6.89 Samsung-compatibility KernelSU Next module was built with CONFIG_KSU_SAMSUNG_RKP=y, CONFIG_KSU_SAMSUNG_DEFEX=y, CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT=y and CONFIG_KSU_SAMSUNG_KDP=n.

The exact KernelSU Next version pinned for this build, commit 159bc7da4266fd9331f63e25901629db4b7bfff8, in kernel/compat/samsung_kdp.c dynamically resolves FIVE functions when KDP is enabled: prepare_ro_creds, kdp_assign_pgd, kdp_usecount_dec_and_test, inc_rlimit_ucounts, dec_rlimit_ucounts. If any is absent, the KDP initializer returns -ENOENT; kernel/core/init.c propagates failure and prevents module initialization.

Original HEZB1 genuine stock boot.img BTF audit (61,049 FUNC records) established:

| Required function | Present in original stock BTF? |
| --- | --- |
| prepare_ro_creds | NO |
| kdp_assign_pgd | NO |
| kdp_usecount_dec_and_test | NO |
| inc_rlimit_ucounts | YES |
| dec_rlimit_ucounts | YES |

There are zero function names containing case-insensitive "kdp" in the genuine stock BTF function list. This list was read from the user's original A146P_stock_6.6.89_BTF_and_decompilation_toolkit.zip, stock_btf/btf_func_prototypes.tsv; underlying stock boot.img SHA256 0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9.

Pinned Physwizz 6.6.89 source physwizz/a146p SHA 6560c1ca1f009dd3e53b698245bf2df1b9804e03 code search also found no implementation of the three KDP-specific names; generic ucounts functions do exist. Code search absence and original stock BTF absence do not conclusively establish that the live custom Physwizz kernel or proprietary runtime components lack every KDP capability.

Original stock kernel configuration a146p-stock/stock-A146PXXUHEZB1-6.6.89.config includes CONFIG_SECURITY_DEFEX=y, CONFIG_SECURITY_DEFEX_USER=y and CONFIG_SAMSUNG_GKI_KERNEL=y, but does not list CONFIG_KDP, CONFIG_KDP_NS or CONFIG_RKP.

CONFIG_KSU_SAMSUNG_KDP is not a control to enable extra Samsung protection; it selects KernelSU's special handling of ALREADY-KDP-protected credentials. Enabling that path without the actual helpers would likely prevent KernelSU boot-time initialization. Incorrect KDP ABI can cause memory errors even if names are resolved.

## Termux one-line read-only live verification

    su -c 'for s in prepare_ro_creds kdp_assign_pgd kdp_usecount_dec_and_test inc_rlimit_ucounts dec_rlimit_ucounts commit_creds; do if grep -Eq "[[:space:]]$s([[:space:]]|$)" /proc/kallsyms; then echo "$s PRESENT"; else echo "$s NOT_VISIBLE"; fi; done'

This only reads /proc/kallsyms. NOT_VISIBLE can mean absent OR restricted kallsyms. A name alone does not validate its ABI or initialization safety. Run before removing current root, if available.

## Conclusion

Keep KDP disabled in the Samsung-compatibility Physwizz .ko unless a matching active kernel demonstrates the expected helpers and structure/function ABI. That module remains untested for independent early boot. Samsung-specific stock 6.6.89 ABI validation is a separate and unresolved build objective.

Sources:
- https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/compat/samsung_kdp.c
- https://github.com/KernelSU-Next/KernelSU-Next/blob/159bc7da4266fd9331f63e25901629db4b7bfff8/kernel/core/init.c
- https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/.github/workflows/a146p-samsung-compat-ksu.yml
