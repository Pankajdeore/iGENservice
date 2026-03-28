"""
igen_patcher.py  — iGEN subpage HTML patcher  v4
=================================================
Fully idempotent — every fix checks before applying.
Safe to re-run on both fresh pages AND pages already partially patched.

Usage:
    python3 igen_patcher.py sub  path/to/subpage.html
    python3 igen_patcher.py root path/to/rootpage.html
"""
import sys
import re

MAILTO_LINK = '<a href="mailto:org@igenservice.com" style="color:inherit;">org@igenservice.com</a>'

# ── Dark mode toggle button HTML strings ────────────────────────────
DM_MOBILE = (
    '\n        <!-- Dark mode toggle — mobile -->\n'
    '        <button id="darkToggleMobile" class="dm-toggle d-lg-none" '
    'aria-label="Toggle dark mode" title="Toggle dark mode">'
    '<i class="fa fa-moon"></i></button>'
)
DM_DESKTOP = (
    '\n                <!-- Dark mode toggle — desktop -->\n'
    '                <button id="darkToggle" class="dm-toggle mr-3" '
    'aria-label="Toggle dark mode" title="Toggle dark mode">'
    '<i class="fa fa-moon"></i></button>'
)


def fix_all_emails(html):
    """Replace every form of the iGEN email with a clean mailto: link."""
    html = re.sub(
        r'<a\s+href="[^"]*cdn-cgi/l/email-protection[^"]*"[^>]*>.*?</a>',
        MAILTO_LINK, html, flags=re.DOTALL | re.IGNORECASE
    )
    html = re.sub(
        r'<a\s+[^>]*><span\s+class="__cf_email__"[^>]*>.*?</span>\s*</a>',
        MAILTO_LINK, html, flags=re.DOTALL | re.IGNORECASE
    )
    html = re.sub(
        r'<span\s+class="ig-email"[^>]*data-u="org"[^>]*data-d="igenservice\.com"[^>]*>\s*</span>',
        MAILTO_LINK, html, flags=re.IGNORECASE
    )
    html = re.sub(
        r'href="mailto:org@igenservice\.com"(?!\s+style)',
        'href="mailto:org@igenservice.com" style="color:inherit;"',
        html, flags=re.IGNORECASE
    )
    html = re.sub(
        r'(?<![=\'\"])org@igenservice\.com(?![\'"\w])',
        MAILTO_LINK, html, flags=re.IGNORECASE
    )
    # Flatten double-nested mailto anchors
    html = re.sub(
        r'<a href="mailto:org@igenservice\.com"[^>]*>\s*'
        r'<a href="mailto:org@igenservice\.com"[^>]*>([^<]+)</a>\s*</a>',
        MAILTO_LINK, html, flags=re.IGNORECASE
    )
    return html


MODE = sys.argv[1]   # "sub" or "root"
path = sys.argv[2]

with open(path, "r", encoding="utf-8", errors="replace") as f:
    src = f.read()


# ════════════════════════════════════════════════════════════════════
# ROOT MODE
# ════════════════════════════════════════════════════════════════════
if MODE == "root":
    src = src.replace(
        '<script src="js/main.js"></script>',
        '<script src="js/igencommon.js"></script>'
    )
    src = fix_all_emails(src)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    sys.exit(0)


# ════════════════════════════════════════════════════════════════════
# SUB MODE — full idempotent patch
# Every step checks whether the fix is already present before applying.
# ════════════════════════════════════════════════════════════════════

# 1. Fix Windows backslash paths
def fix_bs(m):
    return m.group(0).replace("\\", "/")
src = re.sub(r'(?:src|href)="[^"]*\\[^"]*"', fix_bs, src)

# 2. Inject igenfix.css into <head>
IGENFIX = '    <link href="../css/igenfix.css" rel="stylesheet">'
if "igenfix.css" not in src:
    src = src.replace("</head>", IGENFIX + "\n</head>", 1)

# 3a. jQuery CDN upgrade
src = re.sub(
    r'<script src="(?:https://code\.jquery\.com/[^"]+|[./]*lib/jquery[^"]*)"[^>]*></script>',
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>',
    src
)
# 3b. Bootstrap JS CDN upgrade
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
# 3g. Remove unused local lib/ scripts
src = re.sub(r'\s*<script src="[./]*lib/(?:easing|waypoints|isotope)[^"]*"></script>', "", src)

# 4. Remove old main.js / mail refs
src = re.sub(r"\s*<script src=\"[./]*js/main\.js\"></script>", "", src)
src = re.sub(r"\s*<script src=\"[./]*mail/[^\"]*\"></script>", "", src)

# 5. Inject igencommon.js before </body>
if "igencommon.js" not in src:
    src = src.replace("</body>",
        '<script src="../js/igencommon.js"></script>\n</body>', 1)

# 6. Fix style.css path
src = re.sub(r'href="css/style\.css"', 'href="../css/style.css"', src)

# 7. Remove hard-coded "active" from About Us link
src = re.sub(
    r'(href="(?:\.\.\/)?about\.html"\s+class="nav-item nav-link)\s+active"',
    r'\1"', src
)

# 8. Fix dropdown typos
src = src.replace("Internet of Things (loT)", "Internet of Things (IoT)")
src = re.sub(r"GenAl(?=[<\s])", "GenAI", src)

# 9. Fix footer copyright link href="#"
src = re.sub(
    r'(href=")#(">(?:iGEN|\s*iGEN\s*)</a>)',
    r'\1../index.html\2', src
)

# 10. Add HTML Codex attribution if missing
if "htmlcodex" not in src.lower():
    CODEX = (
        '        <p class="mb-0 text-white-50" style="font-size:0.85rem;">'
        'Website design adapted from '
        '<a href="https://htmlcodex.com" class="text-white-50" '
        'target="_blank" rel="noopener">HTML Codex</a></p>'
    )
    src = re.sub(r"(All Rights Reserved\.</p>)", r"\1\n" + CODEX, src, count=1)

# 11. Add Privacy Policy quick link if missing
if "privacy.html" not in src:
    PRIV = (
        '                <a class="text-white-50" href="../privacy.html">'
        '<i class="fa fa-angle-right text-primary mr-2"></i>Privacy Policy</a>'
    )
    src = re.sub(
        r"(fa-angle-right text-primary mr-2\"></i>Contact Us</a>)",
        r"\1\n" + PRIV, src, count=1
    )

# 12. Email fix
src = fix_all_emails(src)

# ── 13. DARK MODE TOGGLE BUTTONS ────────────────────────────────────
# Inject directly into the HTML so they appear regardless of JS timing.
# This makes dark mode consistent across ALL subfolders.
# Each injection checks whether the button already exists first.

# 13a. Mobile toggle — insert before the hamburger <button>
if 'id="darkToggleMobile"' not in src:
    src = re.sub(
        r'(<button[^>]+class="navbar-toggler"[^>]*>)',
        DM_MOBILE + r'\n        \1',
        src, count=1
    )

# 13b. Desktop toggle — insert as first child of the d-none d-lg-flex area
if 'id="darkToggle"' not in src:
    src = re.sub(
        r'(<div class="d-none d-lg-flex[^"]*"[^>]*>)',
        r'\1' + DM_DESKTOP,
        src, count=1
    )

# ── 14. Ensure id="mainNav" on the navbar wrapper ───────────────────
# Some pages have the outer div without the id — sticky nav won't work.
if 'id="mainNav"' not in src:
    src = re.sub(
        r'<div class="container-fluid bg-white position-relative">(\s*<nav)',
        r'<div id="mainNav" class="container-fluid bg-white position-relative">\g<1>',
        src, count=1
    )

# ── 15. Ensure nav-logo class on the navbar brand img ───────────────
# Sticky navbar shrink relies on this class.
if 'class="nav-logo"' not in src and 'nav-logo' not in src:
    src = re.sub(
        r'(<img src="[^"]*igenlogo[^"]*"[^>]*)(style="height:60px;")',
        r'\1class="nav-logo" \2',
        src, count=1
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(src)
