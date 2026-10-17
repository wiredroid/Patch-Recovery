# A146P HEZB1 genuine-OEM CRC comparison: next evidence gate (2026-10-17)

## New verified research CI results

- GhostLock Kotlin + native KernelSU Next integration: [CI #38962672236](https://github.com/wiredroid/Patch-Recovery/actions/runs/38962672236) **success**. This only builds/tests app source; no exploit root proof.
- Android ARM64 KernelSU Next ksud with the hash-pinned **experimental** A146P research .ko staged as `android15-6.6_kernelsu.ko`: [CI #38962895723](https://github.com/wiredroid/Patch-Recovery/actions/runs/38962895723) **success**; binary intentionally not distributed.
- Reconstructed partial Google GKI89+Samsung LKM: [CI #38967262315](https://github.com/wiredroid/Patch-Recovery/actions/runs/38967262315) **success**, candidate module release metadata labels `6.6.89-android15-8-abA146PXXUHEZB1-4k`.
- The latest module has **219 ELF imports** and **161 __versions CRC records**, including `module_layout`; all **160 exports imported from the reconstructed kernel** have matching candidate CRCs; the other **59** are nonexported by the *reconstructed* kernel. The exact OEM Module.symvers / CRCs remain UNKNOWN. Adjusting `LOCALVERSION` changes the *metadata label*, not actual binary ABI equivalence.
- Independently confirmed genuine stock boot SHA256 `0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9`. Its embedded gzip kernel Image decompresses to 33,380,864 bytes, SHA256 `8edf4545acc10993e305271c2e05052d60093812d0f3374364d7cf3c8e6b52c7`, banner `Linux version 6.6.89-android15-8-abA146PXXUHEZB1-4k`. This original Image matches the pre-existing stock BTF extraction toolkit; it does *not* yield OEM Module.symvers by itself.
- [CRC comparison CI #39014558152](https://github.com/wiredroid/Patch-Recovery/actions/runs/39014558152) **success**: five synthetic-edge-case tests, plus entire real research 219-import candidate TSV tested against a clearly **SYNTHETIC** three-symbol vendor module fixture, and deliberate one-bit CRC mismatch rejected. Synthetic results are NOT evidence about Samsung OEM CRCs.

## How to collect NEW evidence without touching bootloader or kernel

When the owner is ready, on the currently working rooted Physwizz phone, use a single-line Termux command, without `su` unless the mounted module files require elevated read permissions:

```sh
curl -fL "https://raw.githubusercontent.com/wiredroid/Patch-Recovery/a146p-ksunext-stock-build/a146p-stock/tools/extract-installed-oem-module-crcs.py" -o "$HOME/a146p-installed-vendor-crc.py" && python "$HOME/a146p-installed-vendor-crc.py" --output "/sdcard/Download/A146P-OEM-vendor-module-CRC-evidence.json"
```

The parser **only reads** mounted module ELF .ko files in `/vendor/lib/modules`, `/vendor_dlkm/lib/modules`, `/odm_dlkm/lib/modules` and `/system_dlkm/lib/modules`. It *does not* load modules or trigger GhostLock; it records symbols, CRCs, matched release and conflicts. It can return no matching release evidence if the device partitions do not contain HEZB1 versioned modules; this is a valid negative/inconclusive result, not a reason to flash.

The installed module set may be modified; `vermagic` equality alone cannot authenticate genuine OEM bytes. For strongest provenance, extract matching vendor_dlkm.img.lz4 / vendor_dlkm module files from the user's **original A146PXXUHEZB1 AP firmware package** via a read-only offline PC method, then independently compare hashes/CRCs.

## Compare the newly collected JSON to CI candidate imports

After transferring the generated JSON file and the candidate import TSV from CI #38967262315, run:

```sh
python3 a146p-stock/tools/compare-oem-vendor-module-crcs.py --candidate-tsv candidate-import-audit.tsv --reference-json A146P-OEM-vendor-module-CRC-evidence.json --output report/oem-crc-comparison
```

The comparator reports per-symbol matched, mismatched, conflicting or unavailable CRCs, and fails closed if any mismatch/conflict or no overlapping CRC evidence is present. Even a 100% reference match does NOT prove stock module load compatibility or a locked-bootloader exploit. The word `OEM` in the collected JSON filename is a *target label*, not verified provenance.

## End goal and boundary

A compatible research .ko and an embeddable ksud are necessary but not sufficient for runtime module insertion on actual OEM stock. Still unverified: physical security/runtime protections, 59 nonexported references, original Samsung module version CRCs, GhostLock device primitive success and persistence/reboot strategy. Do **not** relock bootloader or replace running Physwizz boot/init_boot to collect CRCs.
