# Exact HEZB1 stock BTF anchors for Samsung F2FS source integration

**16 October 2026 (Sydney). Research evidence only, no verified stock-compatible module.**

The original user-owned firmware `boot.img` was re-accessed from the ChatGPT Files Library. Its locally computed SHA-256 was independently checked as
`0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`;
original `init_boot.img` SHA-256 was checked as
`a514ef26365ff0e92871e74d2e87f1da5a4461e4e40e0b7d4cebdf72a18d4976`.
Neither image was modified or uploaded to GitHub.

A previously extracted toolkit `A146P_stock_6.6.89_BTF_and_decompilation_toolkit.zip` from the original stock kernel contains `stock_btf/btf_func_prototypes.tsv`, `stock_btf/btf_types.tsv`, and `stock_btf/btf_struct_members.tsv`. The following entries are from that **actual stock kernel BTF**, not from Physwizz or a sibling-device source.

## Shipping stock BTF contains the ported F2FS helper functions

| BTF FUNC type ID | Function name | Actual shipping stock BTF prototype |
| --- | --- | --- |
| 50741 | `print_block_data` | `void print_block_data(struct f2fs_sb_info * sbi, sector_t blocknr, unsigned char * data_to_dump, int start, int len);` |
| 51951 | `f2fs_set_sb_extra_flag` | `void f2fs_set_sb_extra_flag(struct f2fs_sb_info * sbi, int flag);` |
| 51952 | `f2fs_get_fsck_stat` | `void f2fs_get_fsck_stat(struct f2fs_sb_info * sbi);` |
| 50739 | `f2fs_fill_dentries` | `int f2fs_fill_dentries(struct dir_context * ctx, struct f2fs_dentry_ptr * d, unsigned int start_pos, struct fscrypt_str * fstr);` |

These confirm **name and BTF function signature presence only**. In particular, the original compiled **function bodies are not recovered**, and a matching BTF signature alone does not prove symbol export, ABI CRC, security behavior, or loading rights.

## Shipping stock BTF struct/union anchors

| Type | BTF type ID | Shipping size |
| --- | --- | --- |
| `f2fs_inode_info` | 50562 | 1,440 bytes |
| `f2fs_sb_info` | 50601 | 5,992 bytes |
| `f2fs_super_block` | 50603 | 3,072 bytes |
| `f2fs_sec_stat_info` | 50656 | 376 bytes |
| `f2fs_sec_fsck_info` | 50657 | 40 bytes |
| `f2fs_sec_ddp_info` | 50658 | 32 bytes |
| `f2fs_sec_blkops_dbg` | 50660 | 80 bytes |
| `f2fs_sec_heimdallfs_stat` | 50663 | 40 bytes |
| `f2fs_sb_extra_flag_blk` | 51320 | 4,096 bytes |

Selected **bit offsets** for the real stock `f2fs_inode_info`:

- `mtime_cnt` 11040; `is_cache` 11072; `mtime_interval` 11136; `is_force_cold` 11392.
- `gdonate_list` 7680.

Selected **bit offsets** in real `f2fs_sb_info`:

- `sec_reserved_blocks` 14016; `pin_reserved_sec` 20736; `pin_guaranteed_blkaddr` 23296; `truncate_wq` 27520.
- `sec_stat` 35648; `sec_fsck_stat` 38656; `sec_ddp_stat` 38976.
- `s_sec_blkops_total` 39552; `s_sec_dbg_entries` 39680; `s_sec_dbg_max_entry` 46080; `sec_heimdallfs_stat` 46720.
- `logistic_bias` 47040; `logistic_threshold` 47104; `logistic_scale` 47168; `streamid_enable` 47904.

The `f2fs_sb_extra_flag_blk` has 10 named members, with shipping byte offsets:
`need_fsck=0`, `spo_counter=4`, `fsck_read_bytes=8`,
`fsck_written_bytes=16`, `fsck_elapsed_time=24`, `fsck_exit_code=32`,
`valid_node_count=36`, `valid_inode_count=40`, `ddp_stats=44`,
`rsvd=76` (4,020 bytes). This establishes the actual BTF *layout*, not verified on-disk read/write semantics.

## Cross-check with source integration

- The original upstream conservative forward-port did not include all the Samsung source definitions referenced by `fs/f2fs/dir.c`, `namei.c`, or `checkpoint.c`.
- Research overlays: `patches/0001` for `print_block_data`, `patches/0002` for ML stream inode fields, `patches/0003` for F2FS SEC/fsck/stat on-disk structures and helpers. Their declarations now have **BTF evidence from exact stock**; their source bodies remain source-port hypotheses.
- `patches/0003` originally failed `git apply` at EOF of `include/linux/f2fs_fs.h` (run [38782623864](https://github.com/wiredroid/Patch-Recovery/actions/runs/38782623864)), not at compilation. Corrected to match the four **real** final GKI89 lines (commit `c6b5f8531d2ff0a26ff558ecb95132efa2eb47f3`). Rebuild [38785398460](https://github.com/wiredroid/Patch-Recovery/actions/runs/38785398460).
- Source-exactness, struct member offsets of the **candidate**, `Module.symvers` CRCs, `vermagic`, actual stock exported symbol list and Samsung DEFEX/module signature enforcement still require independent checks.
- No attempt was made to load `.ko`, change firmware images, or relock the bootloader.

**Limitations:** BTF layout and prototype matches cannot establish functional equivalence, binary equivalence, symbol visibility/CRC, original signing trust, or that a valid late privileged module loader exists on a locked Samsung device.
