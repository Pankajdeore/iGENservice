"""
igen_patcher.py  — iGEN subpage HTML patcher
Usage:
    python3 igen_patcher.py sub  path/to/subpage.html
    python3 igen_patcher.py root path/to/rootpage.html
"""
import sys
import re


MAILTO_LINK = '<a href="mailto:org@igenservice.com" style="color:inherit;">org@igenservice.com</a>'

def fix_all_emails(html):
    """Replace every form of the iGEN email with a clean mailto: link."""
    # a. CF-encoded anchor: <a href="/cdn-cgi/...">...[email protected]...</a>
    html = re.sub(
        r'<a\s+href="[^"]*cdn-cgi/l/email-protection[^"]*"[^>]*>.*?</a>',
        MAILTO_LINK, html, flags=re.DOTALL | re.IGNORECASE
    )
    # Also handle CF span inside anchor: <a href="..."><span class="__cf_email__"...></span></a>
    html = re.sub(
        r'<a\s+[^>]*><span\s+class="__cf_email__"[^>]*>.*?</span>\s*</a>',
        MAILTO_LINK, html, flags=re.DOTALL | re.IGNORECASE
    )
    # b. Old ig-email span from previous patcher
    html = re.sub(
        r'<span\s+class="ig-email"[^>]*data-u="org"[^>]*data-d="igenservice\.com"[^>]*>\s*</span>',
        MAILTO_LINK, html, flags=re.IGNORECASE
    )
    # c. Standalone mailto: href without visible text (href only)
    html = re.sub(
        r'href="mailto:org@igenservice\.com"',
        'href="mailto:org@igenservice.com" style="color:inherit;"',
        html, flags=re.IGNORECASE
    )
    # d. Plain bare email text not already inside an attribute value
    html = re.sub(
        r'(?<![=\'\"])org@igenservice\.com(?![\'"\w])',
        MAILTO_LINK, html, flags=re.IGNORECASE
    )
    # e. Flatten any double-nested mailto anchors created by multi-pass
    html = re.sub(
        r'<a href="mailto:org@igenservice\.com"[^>]*>\s*<a href="mailto:org@igenservice\.com"[^>]*>([^<]+)</a>\s*</a>',
        MAILTO_LINK, html, flags=re.IGNORECASE
    )
    return html

MODE = sys.argv[1]   # "sub" or "root"
path = sys.argv[2]

with open(path, "r", encoding="utf-8", errors="replace") as f:
    src = f.read()

# ─── ROOT MODE: only swap main.js reference ────────────────────────
if MODE == "root":
    # Swap main.js → igencommon.js
    src = src.replace(
        '<script src="js/main.js"></script>',
        '<script src="js/igencommon.js"></script>'
    )
    # Apply email fix to root pages too
    src = fix_all_emails(src)
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

# 12. EMAIL FIX
# Now that Cloudflare Email Obfuscation is OFF, use a plain mailto: link.
# Also handles any ig-email spans from previous patcher runs.
src = fix_all_emails(src)

with open(path, "w", encoding="utf-8") as f:
    f.write(src)
