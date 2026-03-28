#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# patch-subpages.sh — iGEN website universal fix patcher  v4
# ════════════════════════════════════════════════════════════════════
# Run from the ROOT of your iGENservice repo:
#   chmod +x patch-subpages.sh
#   ./patch-subpages.sh
#
# Requires: python3 + igen_patcher.py in the same folder.
#
# Skip condition: file already has id="darkToggle" in the HTML.
# This means pages patched by an older version (which only had
# igencommon.js but no toggle buttons) will be re-processed.
# ════════════════════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 not found.${NC}"; exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCHER="$SCRIPT_DIR/igen_patcher.py"

if [ ! -f "$PATCHER" ]; then
    echo -e "${RED}ERROR: igen_patcher.py not found.${NC}"; exit 1
fi

SUBFOLDERS=("services" "technology" "coe")
PATCHED=0; SKIPPED=0

echo ""; echo "═══════════════════════════════════════════"
echo "  iGEN website — universal patch script v4"
echo "═══════════════════════════════════════════"; echo ""

patch_subpage() {
    local FILE="$1"
    # Skip only if dark toggle is already in the HTML
    # (older patches only had igencommon.js — those will be re-processed)
    if grep -q 'id="darkToggle"' "$FILE" 2>/dev/null; then
        echo -e "  ${YELLOW}SKIP${NC}  $FILE  (fully patched)"
        (( SKIPPED++ )) || true; return
    fi
    echo -e "  ${GREEN}PATCH${NC} $FILE"
    python3 "$PATCHER" sub "$FILE"
    (( PATCHED++ )) || true
}

patch_root() {
    local FILE="$1"
    if grep -q "igencommon.js" "$FILE" 2>/dev/null; then
        # Root pages: also re-run if email is still plain text
        if grep -q 'org@igenservice\.com[^<]*<' "$FILE" 2>/dev/null; then
            echo -e "  ${GREEN}PATCH${NC} $FILE  (root — email fix)"
            python3 "$PATCHER" root "$FILE"
            (( PATCHED++ )) || true
        else
            echo -e "  ${YELLOW}SKIP${NC}  $FILE  (root — already patched)"
            (( SKIPPED++ )) || true
        fi
        return
    fi
    grep -q "js/main.js" "$FILE" 2>/dev/null || return 0
    echo -e "  ${GREEN}PATCH${NC} $FILE  (root)"
    python3 "$PATCHER" root "$FILE"
    (( PATCHED++ )) || true
}

echo "Patching subfolder pages..."; echo ""
for FOLDER in "${SUBFOLDERS[@]}"; do
    if [ -d "$FOLDER" ]; then
        echo "  Folder: $FOLDER/"
        for FILE in "$FOLDER"/*.html; do
            [ -f "$FILE" ] || continue
            patch_subpage "$FILE"
        done
        echo ""
    else
        echo -e "  ${RED}WARN${NC}  '$FOLDER/' not found — skipping"
    fi
done

echo "Checking root-level pages..."; echo ""
for FILE in *.html; do
    [ -f "$FILE" ] || continue
    patch_root "$FILE"
done

echo ""; echo "═══════════════════════════════════════════"
printf "  Done.  Patched: ${GREEN}%d${NC}   Skipped: ${YELLOW}%d${NC}\n" "$PATCHED" "$SKIPPED"
echo "═══════════════════════════════════════════"; echo ""
echo "Next steps:"
echo "  git add -A"
echo '  git commit -m "Fix dark mode toggle consistency across all subfolders"'
echo "  git push"; echo ""
