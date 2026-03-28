#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# patch-subpages.sh — iGEN website universal fix patcher  v2
# ════════════════════════════════════════════════════════════════════
#
# Run this ONCE from the ROOT of your iGENservice repo:
#
#   chmod +x patch-subpages.sh
#   ./patch-subpages.sh
#
# Works on macOS and Linux. Requires python3 (standard on both).
#
# What it fixes in every .html file inside services/, technology/, coe/:
#   1.  Backslash paths  img\foo.jpg  →  img/foo.jpg
#   2.  Injects  <link href="../css/igenfix.css">  into <head>
#   3.  Replaces old local lib/ script/link tags with CDN equivalents
#   4.  Removes old js/main.js reference (igencommon replaces it)
#   5.  Injects  <script src="../js/igencommon.js">  before </body>
#   6.  Fixes css/style.css path  →  ../css/style.css
#   7.  Removes hard-coded "active" class from About Us nav link
#   8.  Fixes "loT" typo → "IoT" and "GenAl" typo → "GenAI"
#   9.  Fixes broken footer copyright link  href="#"  →  ../index.html
#  10.  Adds HTML Codex attribution if missing (licence compliance)
#  11.  Adds Privacy Policy quick link to footer if missing
#
# Root-level pages: swaps js/main.js → js/igencommon.js only.
# Safe to re-run — skips files that already contain igencommon.js.
# ════════════════════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 is required but not found.${NC}"
    echo "Mac:   brew install python3"
    echo "Linux: sudo apt install python3"
    exit 1
fi

SUBFOLDERS=("services" "technology" "coe")
PATCHED=0
SKIPPED=0

echo ""
echo "═══════════════════════════════════════════"
echo "  iGEN website — universal patch script v2"
echo "═══════════════════════════════════════════"
echo ""

# ─── Python patcher — all text manipulation done here ──────────────
# Written to a temp file so heredoc quoting is simple and reliable.
PATCHER=$(mktemp /tmp/igen_patcher_XXXX.py)
trap 'rm -f "$PATCHER"' EXIT

cat > "$PATCHER" << 'PYEOF'
import sys, re

MODE = sys.argv[1]   # "sub" or "root"
path = sys.argv[2]

with open(path, 'r', encoding='utf-8', errors='replace') as f:
    src = f.read()

if MODE == "root":
    # Root pages: only swap main.js → igencommon.js
    src = src.replace(
        '<script src="js/main.js"></script>',
        '<script src="js/igencommon.js"></script>'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    sys.exit(0)

# ── SUB-PAGE PATCHES ─────────────────────────────────────────────────

# 1. Fix Windows backslash paths in src="..." and href="..."
def fix_bs(m):
    return m.group(0).replace('\\', '/')
src = re.sub(r'(?:src|href)="[^"]*\\[^"]*"', fix_bs, src)

# 2. Inject igenfix.css before </head>
IGENFIX = '    <link href="../css/igenfix.css" rel="stylesheet">'
if 'igenfix.css' not in src:
    src = src.replace('</head>', IGENFIX + '\n</head>', 1)

# 3a. jQuery — old CDN or local lib/
src = re.sub(
    r'<script src="(?:https://code\.jquery\.com/[^"]+|[./]*lib/jquery[^"]*)"[^>]*></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>',
    src
)

# 3b. Bootstrap JS — old CDN or local lib/
src = re.sub(
    r'<script src="(?:https://stackpath\.bootstrapcdn\.com/[^"]+|[./]*lib/bootstrap[^"]*)"[^>]*></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.2/js/bootstrap.bundle.min.js"></script>',
    src
)

# 3c. OwlCarousel JS local → CDN
src = re.sub(
    r'<script src="[./]*lib/owlcarousel/owl\.carousel\.min\.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js"></script>',
    src
)

# 3d. OwlCarousel CSS local → CDN
src = re.sub(
    r'href="[./]*lib/owlcarousel/assets/owl\.carousel\.min\.css"',
    'href="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/assets/owl.carousel.min.css"',
    src
)

# 3e. Lightbox JS local → CDN
src = re.sub(
    r'<script src="[./]*lib/lightbox/js/lightbox\.min\.js"></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.4/js/lightbox.min.js"></script>',
    src
)

# 3f. Lightbox CSS local → CDN
src = re.sub(
    r'href="[./]*lib/lightbox/css/lightbox\.min\.css"',
    'href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.4/css/lightbox.min.css"',
    src
)

# 3g. Remove unused lib/ scripts (easing, waypoints, isotope)
src = re.sub(r'\s*<script src="[./]*lib/(?:easing|waypoints|isotope)[^"]*"></script>', '', src)

# 4. Remove old main.js / mail/contact.js references
src = re.sub(r'\s*<script src="[./]*js/main\.js"></script>', '', src)
src = re.sub(r'\s*<script src="[./]*mail/[^"]*"></script>', '', src)

# 5. Inject igencommon.js before </body>
COMMON = '<script src="../js/igencommon.js"></script>'
if 'igencommon.js' not in src:
    src = src.replace('</body>', COMMON + '\n</body>', 1)

# 6. Fix style.css path
src = re.sub(r'href="css/style\.css"', 'href="../css/style.css"', src)

# 7. Remove hard-coded "active" from About Us nav link
src = re.sub(
    r'(href="(?:\.\./)?about\.html"\s+class="nav-item nav-link)\s+active"',
    r'\1"', src
)

# 8. Fix known dropdown typos
src = src.replace('Internet of Things (loT)', 'Internet of Things (IoT)')
src = re.sub(r'GenAl(?=[<\s])', 'GenAI', src)

# 9. Fix broken footer copyright link href="#" → ../index.html
#    Targets the iGEN anchor inside the © paragraph
src = re.sub(
    r'(©[^<]*<a\s+href=")#(">[^<]*iGEN)',
    r'\1../index.html\2',
    src
)

# 10. Add HTML Codex attribution if missing
if 'htmlcodex' not in src.lower():
    CODEX = ('        <p class="mb-0 text-white-50" style="font-size:0.85rem;">'
             'Website design adapted from '
             '<a href="https://htmlcodex.com" class="text-white-50" '
             'target="_blank" rel="noopener">HTML Codex</a></p>')
    src = re.sub(
        r'(All Rights Reserved\.</p>)',
        r'\1\n' + CODEX,
        src, count=1
    )

# 11. Add Privacy Policy quick link if missing
if 'privacy.html' not in src:
    PRIV = ('                <a class="text-white-50" href="../privacy.html">'
            '<i class="fa fa-angle-right text-primary mr-2"></i>'
            'Privacy Policy</a>')
    src = re.sub(
        r'(fa-angle-right text-primary mr-2"></i>Contact Us</a>)',
        r'\1\n' + PRIV,
        src, count=1
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
PYEOF

# ════════════════════════════════════════════════════════════════════
patch_subpage() {
    local FILE="$1"
    if grep -q "igencommon.js" "$FILE" 2>/dev/null; then
        echo -e "  ${YELLOW}SKIP${NC}  $FILE  (already patched)"
        (( SKIPPED++ )) || true
        return
    fi
    echo -e "  ${GREEN}PATCH${NC} $FILE"
    python3 "$PATCHER" sub "$FILE"
    (( PATCHED++ )) || true
}

patch_root() {
    local FILE="$1"
    if grep -q "igencommon.js" "$FILE" 2>/dev/null; then
        echo -e "  ${YELLOW}SKIP${NC}  $FILE  (already patched)"
        (( SKIPPED++ )) || true
        return
    fi
    grep -q "js/main.js" "$FILE" 2>/dev/null || return 0
    echo -e "  ${GREEN}PATCH${NC} $FILE  (root)"
    python3 "$PATCHER" root "$FILE"
    (( PATCHED++ )) || true
}

# ─── Run ─────────────────────────────────────────────────────────────
echo "Patching subfolder pages..."
echo ""

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

echo "Checking root-level pages..."
echo ""
for FILE in *.html; do
    [ -f "$FILE" ] || continue
    patch_root "$FILE"
done

echo ""
echo "═══════════════════════════════════════════"
printf "  Done.  Patched: ${GREEN}%d${NC}   Skipped: ${YELLOW}%d${NC}\n" "$PATCHED" "$SKIPPED"
echo "═══════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  git add -A"
echo '  git commit -m "Fix all subpages: CDN libs, dark mode, sticky nav, footer, typos"'
echo "  git push"
echo ""
