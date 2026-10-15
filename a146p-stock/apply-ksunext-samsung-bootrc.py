#!/usr/bin/env python3
"""Patch pinned KernelSU Next 3.4.2 for Samsung read-only syscall table.

Experimental: restore Android init.rc startup injection without writing into
Samsung-protected kernel text/rodata. Applies only to the pinned KSU tree.
This is NOT a boot-tested fix. No device partition writes are performed here.
"""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: apply-ksunext-samsung-bootrc.py <KSU source root>")

p = Path(sys.argv[1]) / "kernel/runtime/ksud_integration.c"
src = p.read_text()

def replace_once(needle: str, replacement: str) -> None:
    global src
    count = src.count(needle)
    if count != 1:
        raise SystemExit(f"ABORT: expected exactly 1 source anchor, found {count}: {needle[:90]!r}")
    src = src.replace(needle, replacement, 1)

# In the Samsung kprobe path the module RC is read on first ordinary file
# read's EOF, NOT from within the kprobe (where filesystem I/O may sleep).
replace_once(
    '    pr_info("read_proxy: orig read finished, start append rc\\n");',
    '''#if defined(CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT) && defined(__aarch64__)
    load_module_rc_once();
#endif
    pr_info("read_proxy: orig read finished, start append rc\\\\n");'''.replace('\\\\n', '\\n') # keeps the C source literal backslash+n
)
replace_once(
    '    pr_info("read_iter_proxy: orig read finished, start append rc\\n");',
    '''#if defined(CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT) && defined(__aarch64__)
    load_module_rc_once();
#endif
    pr_info("read_iter_proxy: orig read finished, start append rc\\\\n");'''.replace('\\\\n', '\\n')
)

block = r'''
#if defined(CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT) && defined(__aarch64__)
/*
 * Samsung protected kernel: no syscall-table or kernel-text patching.
 *
 * A kprobe on vfs_read can recognize Android init's one known init.rc read
 * and point that *open file* at KernelSU's existing per-file read proxy.
 * The kprobe handler must never sleep, open files or unhook itself.
 * load_module_rc_once() is therefore deferred to read_proxy's EOF path.
 */
static bool samsung_rc_installed;
static bool samsung_rc_read_probe_registered;
static bool samsung_rc_fstat_probe_registered;

static int samsung_rc_read_pre(struct kprobe *probe, struct pt_regs *regs)
{
    struct file *file = (struct file *)PT_REGS_PARM1(regs);

    (void)probe;
    if (READ_ONCE(samsung_rc_installed) || strcmp(current->comm, "init"))
        return 0;
    if (!file || !is_init_rc(file))
        return 0;
    if (!file->f_op || (!file->f_op->read && !file->f_op->read_iter))
        return 0;

    memcpy(&fops_proxy, file->f_op, sizeof(fops_proxy));
    orig_read = file->f_op->read;
    orig_read_iter = file->f_op->read_iter;
    if (orig_read)
        fops_proxy.read = read_proxy;
    if (orig_read_iter)
        fops_proxy.read_iter = read_iter_proxy;
    file->f_op = &fops_proxy;
    WRITE_ONCE(samsung_rc_installed, true);
    pr_info("Samsung boot RC: installed per-file init.rc read proxy\n");
    return 0;
}

static struct kprobe samsung_rc_read_probe = {
    .symbol_name = "vfs_read",
    .pre_handler = samsung_rc_read_pre,
};

struct samsung_rc_fstat_state {
    void __user *statbuf;
};

static int samsung_rc_fstat_enter(struct kretprobe_instance *ri,
                                 struct pt_regs *regs)
{
    struct samsung_rc_fstat_state *state = (void *)ri->data;
    struct pt_regs *sysregs = PT_REAL_REGS(regs);
    struct file *file;

    if (strcmp(current->comm, "init") || !sysregs)
        return 1;
    file = fget((unsigned int)PT_REGS_SYSCALL_PARM1(sysregs));
    if (!file)
        return 1;
    if (!is_init_rc(file)) {
        fput(file);
        return 1;
    }
    state->statbuf = (void __user *)PT_REGS_PARM2(sysregs);
    fput(file);
    return 0;
}

static int samsung_rc_fstat_return(struct kretprobe_instance *ri,
                                  struct pt_regs *regs)
{
    struct samsung_rc_fstat_state *state = (void *)ri->data;
    void __user *p;
    long size;

    if (regs_return_value(regs) != 0 || !state->statbuf)
        return 0;
    p = (char __user *)state->statbuf + offsetof(struct stat, st_size);
    if (!copy_from_user_nofault(&size, p, sizeof(size))) {
        long new_size = size + ksu_rc_len;
        if (copy_to_user_nofault(p, &new_size, sizeof(new_size)))
            pr_warn("Samsung boot RC: failed to expand init.rc stat size\n");
    }
    return 0;
}

static struct kretprobe samsung_rc_fstat_probe = {
    .entry_handler = samsung_rc_fstat_enter,
    .handler = samsung_rc_fstat_return,
    .data_size = sizeof(struct samsung_rc_fstat_state),
    .maxactive = 8,
};

static void ksu_samsung_boot_rc_init(void)
{
    int ret;

    if (!ksu_syscall_table) {
        pr_err("Samsung boot RC: syscall table unavailable\n");
        return;
    }
    samsung_rc_fstat_probe.kp.addr =
        (kprobe_opcode_t *)READ_ONCE(ksu_syscall_table[__NR_fstat]);
    ret = register_kretprobe(&samsung_rc_fstat_probe);
    if (ret)
        pr_err("Samsung boot RC: fstat kretprobe failed: %d\n", ret);
    else
        samsung_rc_fstat_probe_registered = true;

    ret = register_kprobe(&samsung_rc_read_probe);
    if (ret)
        pr_err("Samsung boot RC: vfs_read kprobe failed: %d\n", ret);
    else
        samsung_rc_read_probe_registered = true;
}

static void ksu_samsung_boot_rc_exit(void)
{
    if (samsung_rc_read_probe_registered)
        unregister_kprobe(&samsung_rc_read_probe);
    if (samsung_rc_fstat_probe_registered)
        unregister_kretprobe(&samsung_rc_fstat_probe);
}
#endif

'''
replace_once(
    '// ksud: module support\nvoid __init ksu_ksud_init()',
    block + '// ksud: module support\nvoid __init ksu_ksud_init()'
)
replace_once(
    '    ksu_syscall_table_hook(__NR_read, ksu_sys_read, &orig_sys_read);\n    ksu_syscall_table_hook(__NR_fstat, ksu_sys_fstat, &orig_sys_fstat);',
    '''#if defined(CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT) && defined(__aarch64__)
    ksu_samsung_boot_rc_init();
#else
    ksu_syscall_table_hook(__NR_read, ksu_sys_read, &orig_sys_read);
    ksu_syscall_table_hook(__NR_fstat, ksu_sys_fstat, &orig_sys_fstat);
#endif'''
)
replace_once(
    '    unregister_kprobe(&input_event_kp);\n\n    if (module_rc_buf) {',
    '''    unregister_kprobe(&input_event_kp);
#if defined(CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT) && defined(__aarch64__)
    ksu_samsung_boot_rc_exit();
#endif

    if (module_rc_buf) {'''
)
assert "ksu_samsung_boot_rc_init();" in src
assert "load_module_rc_once();" in src
assert "samsung_rc_read_probe" in src
p.write_text(src)
print("Samsung boot RC kprobe patch applied to", p)
