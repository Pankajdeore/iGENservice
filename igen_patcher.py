"""
igen_patcher.py  — iGEN subpage HTML patcher
Usage:
    python3 igen_patcher.py sub  path/to/subpage.html
    python3 igen_patcher.py root path/to/rootpage.html
"""
import sys
import re

MODE = sys.argv[1]   # "sub" or "root"
path = sys.argv[2]

with open(path, "r", encoding="utf-8", errors="replace") as f:
    src = f.read()

# ─── ROOT MODE: only swap main.js reference ────────────────────────
if MODE == "root":
    src = src.replace(
        '<script src="js/main.js"></script>',
        '<script src="js/igencommon.js"></script>'
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    sys.exit(0)

# ─── SUB MODE: full patch ─────────────────────────────────────────

# 1. Fix Windows backslash paths in src="..." and href="..."
def fix_bs(m):
    return m.group(0).replace("\\", "/")
src = re.sub(r'(?:src|href)="[^"]*\\[^"]*"', fix_bs, src)

# 2. Inject igenfix.css before </head>
IGENFIX = '    <link href="../css/igenfix.css" rel="stylesheet">'
if "igenfix.css" not in src:
    src = src.replace("</head>", IGENFIX + "\n</head>", 1)

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
src = re.sub(r'\s*<script src="[./]*lib/(?:easing|waypoints|isotope)[^"]*"></script>', "", src)

# 4. Remove old main.js / mail/contact.js references
src = re.sub(r"\s*<script src=\"[./]*js/main\.js\"></script>", "", src)
src = re.sub(r"\s*<script src=\"[./]*mail/[^\"]*\"></script>", "", src)

# 5. Inject igencommon.js before </body>
COMMON = '<script src="../js/igencommon.js"></script>'
if "igencommon.js" not in src:
    src = src.replace("</body>", COMMON + "\n</body>", 1)

# 6. Fix style.css path
src = re.sub(r'href="css/style\.css"', 'href="../css/style.css"', src)

# 7. Remove hard-coded "active" from About Us nav link
src = re.sub(
    r'(href="(?:\.\.\/)?about\.html"\s+class="nav-item nav-link)\s+active"',
    r'\1"', src
)

# 8. Fix known dropdown typos
src = src.replace("Internet of Things (loT)", "Internet of Things (IoT)")
src = re.sub(r"GenAl(?=[<\s])", "GenAI", src)

# 9. Fix broken footer copyright link href="#" → ../index.html
src = re.sub(
    r'(href=")#(">(?:iGEN|\s*iGEN\s*)</a>)',
    r'\1../index.html\2',
    src
)

# 10. Add HTML Codex attribution if missing (licence compliance)
if "htmlcodex" not in src.lower():
    CODEX = (
        '        <p class="mb-0 text-white-50" style="font-size:0.85rem;">'
        'Website design adapted from '
        '<a href="https://htmlcodex.com" class="text-white-50" '
        'target="_blank" rel="noopener">HTML Codex</a></p>'
    )
    src = re.sub(
        r"(All Rights Reserved\.</p>)",
        r"\1\n" + CODEX,
        src, count=1
    )

# 11. Add Privacy Policy quick link if missing
if "privacy.html" not in src:
    PRIV = (
        '                <a class="text-white-50" href="../privacy.html">'
        '<i class="fa fa-angle-right text-primary mr-2"></i>'
        "Privacy Policy</a>"
    )
    src = re.sub(
        r"(fa-angle-right text-primary mr-2\"></i>Contact Us</a>)",
        r"\1\n" + PRIV,
        src, count=1
    )

# 12. EMAIL FIX — bypass Cloudflare Email Obfuscation
#
# Cloudflare scans HTML for plain email addresses and replaces them
# with encoded anchors like:
#   <a href="/cdn-cgi/l/email-protection" class="__cf_email__"
#      data-cfemail="HEX">[email protected]</a>
#
# Strategy: replace all forms of the plain email with a data-attribute
# span that Cloudflare cannot detect. igencommon.js then assembles it
# into a proper mailto link at runtime.
#
# CF-proof span format:
#   <span class="ig-email" data-u="org" data-d="igenservice.com"></span>
#
# NOTE: The permanent fix is to also disable Email Obfuscation in the
# Cloudflare dashboard: Websites → domain → Scrape Shield →
# Email Address Obfuscation → OFF.

EMAIL_SPAN = (
    '<span class="ig-email" data-u="org" data-d="igenservice.com"></span>'
)

# 12a. Replace mailto: href links that also show the email as text
# Matches: <a href="mailto:org@igenservice.com">org@igenservice.com</a>
src = re.sub(
    r'<a\s+href="mailto:org@igenservice\.com"[^>]*>\s*org@igenservice\.com\s*</a>',
    EMAIL_SPAN,
    src,
    flags=re.IGNORECASE
)

# 12b. Replace standalone mailto: href (link text may differ)
src = re.sub(
    r'href="mailto:org@igenservice\.com"',
    'href="#" class="ig-email" data-u="org" data-d="igenservice.com"',
    src,
    flags=re.IGNORECASE
)

# 12c. Replace any remaining bare email text not inside a tag attribute
# Uses a lookbehind/lookahead to avoid touching values already inside quotes
src = re.sub(
    r'(?<!=")org@igenservice\.com(?!")',
    EMAIL_SPAN,
    src,
    flags=re.IGNORECASE
)

with open(path, "w", encoding="utf-8") as f:
    f.write(src)
