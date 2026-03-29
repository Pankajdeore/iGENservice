"""
fix_all_pages.py  —  iGEN website: fix everything, all at once
==============================================================
Run this script ONCE from the ROOT of your iGENservice repo:

    python3 fix_all_pages.py

It will directly edit every HTML file in services/, technology/, coe/
with ALL fixes applied — dark mode toggles, igenfix.css, CDN scripts,
email links, sticky nav, footer fixes, typo corrections, and more.

No other files needed. No shell scripts. No skip logic that gets in the way.
Every fix checks whether it's already present before applying (idempotent).

After it finishes:
    git add -A
    git commit -m "Fix all subpages: dark mode, nav, email, footer"
    git push
"""

import os
import re
import glob

# ── Constants ────────────────────────────────────────────────────────

IGENFIX_LINK   = '    <link href="../css/igenfix.css" rel="stylesheet">'
IGENCOMMON_TAG = '<script src="../js/igencommon.js"></script>'
MAILTO_LINK    = ('<a href="mailto:org@igenservice.com" '
                  'style="color:inherit;">org@igenservice.com</a>')

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

CODEX_ATTR = (
    '        <p class="mb-0 text-white-50" style="font-size:0.85rem;">'
    'Website design adapted from '
    '<a href="https://htmlcodex.com" class="text-white-50" '
    'target="_blank" rel="noopener">HTML Codex</a></p>'
)

PRIV_LINK = (
    '                <a class="text-white-50" href="../privacy.html">'
    '<i class="fa fa-angle-right text-primary mr-2"></i>'
    'Privacy Policy</a>'
)

# ── Helpers ──────────────────────────────────────────────────────────

def fix_emails(src):
    """Replace every form of the email address with a clean mailto: link."""
    # CF-encoded anchors
    src = re.sub(
        r'<a\s+href="[^"]*cdn-cgi/l/email-protection[^"]*"[^>]*>.*?</a>',
        MAILTO_LINK, src, flags=re.DOTALL | re.IGNORECASE
    )
    src = re.sub(
        r'<a\s+[^>]*><span\s+class="__cf_email__"[^>]*>.*?</span>\s*</a>',
        MAILTO_LINK, src, flags=re.DOTALL | re.IGNORECASE
    )
    # Old ig-email spans
    src = re.sub(
        r'<span\s+class="ig-email"[^>]*>\s*</span>',
        MAILTO_LINK, src, flags=re.IGNORECASE
    )
    # Plain mailto href missing style
    src = re.sub(
        r'href="mailto:org@igenservice\.com"(?!\s+style)',
        'href="mailto:org@igenservice.com" style="color:inherit;"',
        src, flags=re.IGNORECASE
    )
    # Bare plain text email
    src = re.sub(
        r'(?<![=\'"])org@igenservice\.com(?![\'"\w])',
        MAILTO_LINK, src, flags=re.IGNORECASE
    )
    # Flatten any double-nested anchors
    src = re.sub(
        r'<a href="mailto:org@igenservice\.com"[^>]*>\s*'
        r'<a href="mailto:org@igenservice\.com"[^>]*>([^<]+)</a>\s*</a>',
        MAILTO_LINK, src, flags=re.IGNORECASE
    )
    return src


def patch_subpage(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        src = f.read()

    original = src
    fixes = []

    # 1. Fix backslash paths
    def fix_bs(m):
        return m.group(0).replace('\\', '/')
    src = re.sub(r'(?:src|href)="[^"]*\\[^"]*"', fix_bs, src)

    # 2. igenfix.css in <head>
    if 'igenfix.css' not in src:
        src = src.replace('</head>', IGENFIX_LINK + '\n</head>', 1)
        fixes.append('igenfix.css')

    # 3. CDN upgrades
    src = re.sub(
        r'<script src="(?:https://code\.jquery\.com/[^"]+|[./]*lib/jquery[^"]*)"[^>]*></script>',
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>',
        src
    )
    src = re.sub(
        r'<script src="(?:https://stackpath\.bootstrapcdn\.com/[^"]+|[./]*lib/bootstrap[^"]*)"[^>]*></script>',
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.2/js/bootstrap.bundle.min.js"></script>',
        src
    )
    src = re.sub(
        r'<script src="[./]*lib/owlcarousel/owl\.carousel\.min\.js"></script>',
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js"></script>',
        src
    )
    src = re.sub(
        r'href="[./]*lib/owlcarousel/assets/owl\.carousel\.min\.css"',
        'href="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/assets/owl.carousel.min.css"',
        src
    )
    src = re.sub(
        r'<script src="[./]*lib/lightbox/js/lightbox\.min\.js"></script>',
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.4/js/lightbox.min.js"></script>',
        src
    )
    src = re.sub(
        r'href="[./]*lib/lightbox/css/lightbox\.min\.css"',
        'href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.4/css/lightbox.min.css"',
        src
    )
    src = re.sub(
        r'\s*<script src="[./]*lib/(?:easing|waypoints|isotope)[^"]*"></script>', '', src
    )

    # 4. Remove old main.js / mail refs
    src = re.sub(r'\s*<script src="[./]*js/main\.js"></script>', '', src)
    src = re.sub(r'\s*<script src="[./]*mail/[^"]*"></script>', '', src)

    # 5. igencommon.js before </body>
    if 'igencommon.js' not in src:
        src = src.replace('</body>', IGENCOMMON_TAG + '\n</body>', 1)
        fixes.append('igencommon.js')

    # 6. Fix style.css path
    src = re.sub(r'href="css/style\.css"', 'href="../css/style.css"', src)

    # 7. Remove stray active class from About link
    src = re.sub(
        r'(href="(?:\.\.\/)?about\.html"\s+class="nav-item nav-link)\s+active"',
        r'\1"', src
    )

    # 8. Fix dropdown typos
    src = src.replace('Internet of Things (loT)', 'Internet of Things (IoT)')
    src = re.sub(r'GenAl(?=[<\s])', 'GenAI', src)

    # 9. Fix footer copyright link
    src = re.sub(
        r'(href=")#(">(?:iGEN|\s*iGEN\s*)</a>)',
        r'\1../index.html\2', src
    )

    # 10. HTML Codex attribution
    if 'htmlcodex' not in src.lower():
        src = re.sub(
            r'(All Rights Reserved\.</p>)',
            r'\1\n' + CODEX_ATTR, src, count=1
        )
        fixes.append('codex attr')

    # 11. Privacy Policy link in footer
    if 'privacy.html' not in src:
        src = re.sub(
            r'(fa-angle-right text-primary mr-2"></i>Contact Us</a>)',
            r'\1\n' + PRIV_LINK, src, count=1
        )
        fixes.append('privacy link')

    # 12. Email fix
    src = fix_emails(src)

    # 13. Dark mode toggle — MOBILE (before hamburger button)
    if 'id="darkToggleMobile"' not in src:
        src = re.sub(
            r'(<button[^>]+class="navbar-toggler"[^>]*>)',
            DM_MOBILE + r'\n        \1',
            src, count=1
        )
        fixes.append('dm-mobile toggle')

    # 14. Dark mode toggle — DESKTOP (first child of d-none d-lg-flex area)
    if 'id="darkToggle"' not in src:
        src = re.sub(
            r'(<div[^>]+class="[^"]*d-none d-lg-flex[^"]*"[^>]*>)',
            r'\1' + DM_DESKTOP,
            src, count=1
        )
        fixes.append('dm-desktop toggle')

    # 15. id="mainNav" on navbar wrapper
    if 'id="mainNav"' not in src:
        src = re.sub(
            r'(<div\s+class="container-fluid bg-white position-relative">)(\s*<nav)',
            r'<div id="mainNav" class="container-fluid bg-white position-relative">\2',
            src, count=1
        )
        fixes.append('mainNav id')

    # 16. nav-logo class on navbar brand img
    if 'nav-logo' not in src:
        src = re.sub(
            r'(<img\s+src="[^"]*igenlogo[^"]*"\s+)(alt="[^"]*"\s+)',
            r'\1\2class="nav-logo" ',
            src, count=1
        )
        # Also handle img without alt
        if 'nav-logo' not in src:
            src = re.sub(
                r'(<img\s+src="[^"]*igenlogo[^"]*")',
                r'\1 class="nav-logo"',
                src, count=1
            )
        fixes.append('nav-logo class')

    if src != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(src)
        return fixes
    return []


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print()
    print('════════════════════════════════════════════════')
    print('  iGEN — fix_all_pages.py  (all-in-one patcher)')
    print('════════════════════════════════════════════════')
    print()

    subfolders = ['services', 'technology', 'coe']
    total_files   = 0
    total_changed = 0

    for folder in subfolders:
        if not os.path.isdir(folder):
            print(f'  WARN  {folder}/ not found — skipping')
            continue

        print(f'  📁 {folder}/')
        files = sorted(glob.glob(os.path.join(folder, '*.html')))

        if not files:
            print(f'       (no .html files found)')
            continue

        for fpath in files:
            total_files += 1
            try:
                applied = patch_subpage(fpath)
                if applied:
                    total_changed += 1
                    print(f'  FIXED   {fpath}')
                    for fix in applied:
                        print(f'            + {fix}')
                else:
                    print(f'  OK      {fpath}')
            except Exception as e:
                print(f'  ERROR   {fpath}: {e}')

        print()

    print('════════════════════════════════════════════════')
    print(f'  Done.  {total_changed} files updated out of {total_files} scanned.')
    print('════════════════════════════════════════════════')
    print()
    print('Now run:')
    print('  git add -A')
    print('  git commit -m "Fix all subpages: dark mode, nav, email, footer"')
    print('  git push')
    print()


if __name__ == '__main__':
    main()
