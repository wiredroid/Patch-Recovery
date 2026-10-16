# Samsung A146P HEZB1 — verified candidate CRCs and remaining stock-loader gates

Research note — 2026-10-17. **Not a validated OEM-loadable module. No factory-locked exploit tested.**

## Measured from the corrected research build

- Corrected kernel + KernelSU Next v3.4.2 experimental LKM CI: https://github.com/wiredroid/Patch-Recovery/actions/runs/38942607886
- ELF has 219 undefined imports; 160 are exported by reconstructed PARTIAL GKI89, 59 are not exported by reconstruction.
- Parsed 161 authentic .ko symbol CRC/version records, including module_layout. **All 160 exported imported symbols match the reconstructed (NON-OEM) candidate CRC list (0 mismatches).**
- Stock OEM BTF declares FUNC types for 53 of the 59; this only establishes function declarations, NOT callable addresses or exportability.
- Six unexported/data names requiring other evidence: __tracepoint_sys_enter, init_mm, mntns_operations, selinux_blob_sizes, selinux_state, uts_sem.
- Existing module vermagic was 6.6.89-4k-gebbf6177d5ae-dirty, not exact HEZB1.

## Work committed to the GitHub research branch

- Audit tool: https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/tools/audit-module-import-crcs.py
- Stock-target labelled RESEARCH build workflow: https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/.github/workflows/a146p-stock-6.6.89-abi-build.yml
- Workflow intentionally overrides LOCALVERSION and disables LOCALVERSION_AUTO to generate the OEM-target release *string*. This differs from OEM IKCONFIG and cannot establish actual source ABI equivalence. It has a strict post-build CRC and release gate.
- First attempt: https://github.com/wiredroid/Patch-Recovery/actions/runs/38966261719 failed correctly because generated include/config/auto.conf kept the old release; follow-up enables make prepare synchronization: https://github.com/wiredroid/Patch-Recovery/actions/runs/38966847743 (check outcome before claiming success).
- Read-only installed OEM-release module CRC evidence collector: https://github.com/wiredroid/Patch-Recovery/blob/a146p-ksunext-stock-build/a146p-stock/tools/extract-installed-oem-module-crcs.py

## OEM CRC recovery from original vendor modules

Unmodified Samsung vendor_dlkm/odm_dlkm .ko files may carry actual OEM kernel-export CRCs for symbols they import, without Samsung publishing Module.symvers. We can scan installed vendor modules now while keeping the patched Physwizz boot unchanged. Collector parses only ARM64 ELF module version records, accepts EXACT target OEM HEZB1 vermagic, rejects modules compiled for Physwizz, and writes JSON to /sdcard/Download/A146P-OEM-vendor-module-CRC-evidence.json. It never runs GhostLock, calls init_module, writes partitions, or requests signing credentials.

Termux (single line):

    curl -fL 'https://raw.githubusercontent.com/wiredroid/Patch-Recovery/a146p-ksunext-stock-build/a146p-stock/tools/extract-installed-oem-module-crcs.py' -o "$HOME/a146p-oem-crcs.py" && python "$HOME/a146p-oem-crcs.py"

Read-only output may contain zero matches because of permission/path/version differences. An exact-release string does not authenticate installed modules; later byte-level comparisons against genuine Samsung AP images are needed. Only symbols referenced by actual factory modules will be covered, never the whole OEM Module.symvers.

## Gates still unverified

1. OEM CRC equality, total KMI, driver internals, and the final availability of the 59 non-exported references.
2. Samsung stock CONFIG_MODVERSIONS=y, MODULE_SIG_PROTECT=y, DEFEX, SELinux, protected exports, loader trust and any OEM signature restrictions. CONFIG_MODULE_SIG_FORCE is disabled, but that is not a guarantee that unsigned modules can be loaded.
3. GhostLock's runtime race, privilege escalation and independent module insertion on exact original stock A146PXXUHEZB1. CVE code-pattern presence is insufficient.
4. True physical bootloader-locked verified-boot workflow. No factory-locked A146P exploit/root has been demonstrated.

Do NOT relock, flash stock boot on the working Physwizz setup, alter module signature checks, or load experimental LKM on stock until the missing gates are met.
