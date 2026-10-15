# Original A146PXXUHEZB1 stock Linux 6.6.89 ARM64 binary/BTF ABI evidence

Verified directly from user's original `boot.img`, SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`.

- Kernel gzip starts at `boot.img` offset 4096, decompresses to ARM64 `Image` 33,380,864 bytes, SHA256 `8edf4545acc10993e305271c2e05052d60093812d0f3374364d7cf3c8e6b52c7`.
- Kernel ID: `6.6.89-android15-8-abA146PXXUHEZB1-4k`, compile Android clang 18.
- Actual embedded **.BTF** starts at `Image` offset 23,857,508; 6,143,891 bytes; SHA256 `169aa6aac6c8ff3d78bbda9d1b0942da12c84c2f491fdcbb504c36260090f67e`.
- Fully parsed `141882` stock BTF records: `61049 FUNC`, `33168 FUNC_PROTO`, `11967 STRUCT`, `2286 UNION` (including duplicate BTF types in the raw source). These type records supply C-like function **declarations**, actual compiled struct type/member sizes and offsets. They DO NOT provide function **bodies** or original C source.
- `CONFIG_KALLSYMS_ALL=y`, `CONFIG_KALLSYMS_BASE_RELATIVE=y`, `CONFIG_DEBUG_INFO_BTF=y`, `CONFIG_MODVERSIONS=y`.

## Exact stock BTF ABI anchors

- `task_struct` size **4800**: `stack` +40, `flags` +52, `mm` +1440, `active_mm` +1448, `pid` +1560, `tgid` +1564, `real_cred` +2072, `cred` +2080, `comm` +2096, `thread` +3648.
- `cred` size **184**: `uid` +8, `euid` +24, `fsuid` +32, `cap_effective` +64, `security` +128.
- `file` size **264**: `f_cred` +128, `f_path` +168, `f_inode` +184, `f_op` +192.
- `f2fs_sb_info` size **5992**: `sb` +0, `raw_super` +16, `nm_info` +192, `sm_info` +208, `ckpt` +368, `gc_thread` +2504.
- `f2fs_inode_info` size **1440**: `vfs_inode` +0, `i_flags` +704, `flags` +728.
- `f2fs_super_block` size **3072**; `f2fs_checkpoint` size **192**.
- `defex_context` size **88**: `syscall_no` +0, `task` +8, `cred` +80.

Offsets above are bytes from compiled BTF. Source recompilations should be checked against ALL fields, not just these samples.

## How to use these findings

1. Compile the reconstructed Google GKI 6.6.89 + Samsung sources using stock A146PXXUHEZB1 IKCONFIG, exact toolchain where possible, and extract its `.BTF`. Compare stock and rebuilt BTF full type/member record layouts. Exact member offsets and sizes offer much stronger ABI evidence than matching only kernel version strings.
2. The actual BTF can be rendered as C-style struct declarations by `pahole -F btf stock-btf.bin` or by a custom parser. 61,049 stock function type records can be rendered as C-like function signatures, **not recovered code**.
3. To obtain C-like function **body pseudocode**, additionally reconstruct function addresses via compressed KALLSYMS and run Ghidra ARM64 decompiler against the raw stock Image / symbolized ELF. This may approximate but cannot recreate the identical original source or compiler decisions.
4. Continue resolving the 26 Physwizz-versus-stock unresolved files using source, disassembly and ABI anchors, especially F2FS, Android vendor hooks, DEFEX. Do not incorporate Physwizz patches blindly.
5. No evidence yet establishes a loadable Samsung-stock 6.6.89 `.ko` or root with bootloader locked. Stock firmware must remain Samsung-signed for verified-boot compatibility.

The full parsed BTF, `pahole` struct declarations and Ghidra decompilation script were generated as a portable ZIP in the current conversation; original stock kernel binary was **not** uploaded to GitHub by this document.
