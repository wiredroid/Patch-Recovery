#!/data/data/com.termux/files/usr/bin/bash
# READ-ONLY official GhostLock CVE-2026-43499 static preflight for original OEM boot.
# Never executes GhostLock exploit, never flashes, never changes root/SELinux.
set -Eeuo pipefail
umask 077
BOOT_SHA="0fa1f56be55b5f1c0aaac5855ee0ec9c1f388fe101202a13790b7694d48c20f9"
BIN_SHA="3fc007a084b4f41bebf1e4190ac06edea06ffc44893694d5559f2af8571c5b60"
BASE="https://github.com/YuKongA/ghostlock-app/releases/download/pre-release"
OUT="$HOME/a146p-migration/ghostlock-stock-preflight"
mkdir -p "$OUT"
echo "GhostLock OEM stock 6.6.89 static analysis ONLY. Never executing exploit or flashing."
echo "Current running kernel: $(uname -r)"
echo "Expected stock kernel: 6.6.89-android15-8-abA146PXXUHEZB1-4k"
echo "Looking for original OEM boot.img with known SHA-256 $BOOT_SHA"
BOOT=""
if [ "$#" -ge 1 ]; then
    [ -r "$1" ] || { echo "Boot image not readable: $1" >&2; exit 2; }
    GOT="$(sha256sum "$1" | awk '{print $1}')"
    [ "$GOT" = "$BOOT_SHA" ] || { echo "Wrong boot image SHA. This tool only analyzes the ORIGINAL OEM image, not Physwizz." >&2; exit 2; }
    BOOT="$1"
else
    for dir in "$HOME/a146p-migration" /sdcard/Download /sdcard/Download/a146p-migration /sdcard/Documents; do
        [ -d "$dir" ] || continue
        while IFS= read -r -d '' file; do
            [ -r "$file" ] || continue
            GOT="$(sha256sum "$file" | awk '{print $1}')" || continue
            if [ "$GOT" = "$BOOT_SHA" ]; then BOOT="$file"; break; fi
        done < <(find "$dir" -maxdepth 3 -type f \( -iname '*boot*.img' -o -iname '*.img' \) -size +30M -size -34M -print0 2>/dev/null)
        [ -z "$BOOT" ] || break
    done
fi
if [ -z "$BOOT" ]; then
    echo "Original stock boot.img was not found on device. Place the original, exact 32-MiB Samsung HEZB1 boot.img in /sdcard/Download and rerun this script."
    echo "Expected SHA256: $BOOT_SHA"
    exit 3
fi
echo "VERIFIED ORIGINAL: $BOOT"
BIN="$OUT/ghostlock-extract-android-arm64"
if [ ! -s "$BIN" ] || [ "$(sha256sum "$BIN" | awk '{print $1}')" != "$BIN_SHA" ]; then
    echo "Downloading official ARM64 STATIC EXTRACTOR (NOT exploit)."
    curl -fL --retry 4 --retry-delay 3 --connect-timeout 15 --max-time 180 "$BASE/ghostlock-extract-android-arm64" -o "$BIN.tmp"
    [ "$(sha256sum "$BIN.tmp" | awk '{print $1}')" = "$BIN_SHA" ] || { echo "Extractor hash mismatch; aborting" >&2; exit 4; }
    mv "$BIN.tmp" "$BIN"
fi
chmod 700 "$BIN"
echo "Validated official ARM64 extractor SHA256 $BIN_SHA"
echo "Running non-invasive CVE patch analysis (excludes phone kernel memory writes)..."
set +e
"$BIN" "$BOOT" --analysis --work-dir "$OUT" > "$OUT/analysis.txt" 2>&1
RC=$?
set -e
echo "Analysis exit code: $RC"
echo "========== REPORT =========="
cat "$OUT/analysis.txt"
echo "========== END REPORT =========="
echo "Report retained at: $OUT/analysis.txt"
if [ "$RC" -ne 0 ]; then
    echo "Analysis is INCONCLUSIVE OR FAILED. Do not run an exploit based on this output."
    exit "$RC"
fi
echo "This is a static analysis result, NOT tested locked-bootloader root or a verified A146P GhostLock profile."
