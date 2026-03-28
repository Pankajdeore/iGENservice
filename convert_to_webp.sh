#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# convert_to_webp.sh — iGEN image → WebP batch converter
# ════════════════════════════════════════════════════════════════════
#
# Run from the ROOT of your iGENservice repo:
#
#   chmod +x convert_to_webp.sh
#   ./convert_to_webp.sh
#
# What it does:
#   Converts every .jpg, .jpeg, and .png in:
#     img/           (logos, team photos, hero images)
#     services-images/
#     technology-images/
#     coe-images/
#   into a .webp file in the SAME folder.
#   The originals are NOT deleted — they stay as fallbacks.
#
# Quality:
#   - Photos (.jpg/.jpeg): quality 82  → ~35-50% smaller, visually identical
#   - Logos / PNG:         quality 90  → lossless-ish, preserves sharpness
#   - Logo PNG files use -lossless for pixel-perfect quality
#
# After running this script:
#   Run  python3 add_lazy_loading.py  again — it will detect the .webp
#   files and update all <img src="..."> references automatically.
#
# ── REQUIREMENTS ─────────────────────────────────────────────────────
# Install cwebp (free, from Google):
#
#   Mac:    brew install webp
#   Ubuntu: sudo apt install webp
#   Other:  https://developers.google.com/speed/webp/download
#
# ════════════════════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m'

# ── Check cwebp is installed ─────────────────────────────────────────
if ! command -v cwebp &>/dev/null; then
    echo ""
    echo -e "${RED}ERROR: cwebp not found.${NC}"
    echo ""
    echo "Install it first:"
    echo "  Mac:    brew install webp"
    echo "  Ubuntu: sudo apt install webp"
    echo "  Other:  https://developers.google.com/speed/webp/download"
    echo ""
    exit 1
fi

CONVERTED=0
SKIPPED=0
FAILED=0

# Photo quality (82 = excellent, near-lossless looking, ~40% smaller)
PHOTO_Q=82
# PNG/logo quality (90 = very sharp; logos use lossless)
PNG_Q=90

echo ""
echo "══════════════════════════════════════════════"
echo "  iGEN — batch convert images to WebP"
echo "══════════════════════════════════════════════"
echo ""
echo "  Photo quality : $PHOTO_Q"
echo "  PNG quality   : lossless"
echo ""

# ── Image folders to process ─────────────────────────────────────────
FOLDERS=(
    "img"
    "services-images"
    "technology-images"
    "coe-images"
)

convert_file() {
    local INPUT="$1"
    local EXT="${INPUT##*.}"
    local WEBP="${INPUT%.*}.webp"
    local BASENAME
    BASENAME=$(basename "$INPUT")

    # Skip if webp already exists and is newer than source
    if [ -f "$WEBP" ] && [ "$WEBP" -nt "$INPUT" ]; then
        echo -e "  ${GRAY}SKIP${NC}  $INPUT  (webp up to date)"
        (( SKIPPED++ )) || true
        return
    fi

    # Determine quality settings
    local OPTS
    local EXT_LOWER
    EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')

    case "$EXT_LOWER" in
        png)
            # Logos and icons — use lossless to preserve sharpness
            OPTS="-lossless -q 100"
            ;;
        jpg|jpeg)
            # Photos — lossy with high quality
            OPTS="-q $PHOTO_Q -m 6 -af"
            # -m 6   = slowest/best compression method
            # -af    = auto-filter for sharper edges
            ;;
        *)
            echo -e "  ${YELLOW}SKIP${NC}  $INPUT  (unsupported format)"
            (( SKIPPED++ )) || true
            return
            ;;
    esac

    echo -n -e "  ${GREEN}CONV${NC}  $INPUT  → "

    if cwebp $OPTS "$INPUT" -o "$WEBP" -quiet 2>/dev/null; then
        # Show size comparison
        local SRC_SIZE WEBP_SIZE SAVING
        SRC_SIZE=$(wc -c < "$INPUT" 2>/dev/null || echo 0)
        WEBP_SIZE=$(wc -c < "$WEBP"  2>/dev/null || echo 0)
        if [ "$SRC_SIZE" -gt 0 ]; then
            SAVING=$(( (SRC_SIZE - WEBP_SIZE) * 100 / SRC_SIZE ))
            echo -e "${BASENAME%.*}.webp  ${GRAY}(${SAVING}% smaller)${NC}"
        else
            echo -e "${BASENAME%.*}.webp"
        fi
        (( CONVERTED++ )) || true
    else
        echo -e "${RED}FAILED${NC}"
        (( FAILED++ )) || true
    fi
}

# ── Process each folder ───────────────────────────────────────────────
for FOLDER in "${FOLDERS[@]}"; do
    if [ ! -d "$FOLDER" ]; then
        echo -e "  ${YELLOW}WARN${NC}  '$FOLDER/' not found — skipping"
        continue
    fi

    echo "  Folder: $FOLDER/"

    # Find all jpg, jpeg, png files (case-insensitive)
    while IFS= read -r -d '' FILE; do
        convert_file "$FILE"
    done < <(find "$FOLDER" -maxdepth 2 \
        \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) \
        -print0 | sort -z)

    echo ""
done

echo "══════════════════════════════════════════════"
printf "  Converted: ${GREEN}%d${NC}   Skipped: ${YELLOW}%d${NC}   Failed: ${RED}%d${NC}\n" \
    "$CONVERTED" "$SKIPPED" "$FAILED"
echo "══════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Run:  python3 add_lazy_loading.py"
echo "     (updates <img src> to point to .webp files)"
echo ""
echo "  2. Commit everything:"
echo "     git add -A"
echo '     git commit -m "Add WebP images and lazy loading"'
echo "     git push"
echo ""
echo "Note: originals (.jpg/.png) are kept as fallbacks."
echo "You can delete them after confirming everything looks"
echo "correct on the live site."
echo ""
