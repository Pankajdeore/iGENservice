"""
add-lazy-loading.py  —  iGEN website image optimisation, Step 1
================================================================
Adds  loading="lazy"  to every <img> tag that should be lazy-loaded.

Rules:
  - SKIP the logo (igenlogo.png) — it appears in the navbar (LCP area)
  - SKIP the hero image (aboutedited.png) — it IS the LCP element
  - SKIP any img that already has loading="lazy" or loading="eager"
  - ADD loading="lazy" to everything else (team photos, service images,
    technology images, COE images, about-section images)

Run from the ROOT of your iGENservice repo:
    python3 add-lazy-loading.py

Safe to re-run — skips already-tagged images.
"""

import re
import os
import glob

# Images that should NEVER get lazy loading (above-the-fold / LCP)
LCP_IMAGES = {
    "igenlogo.png",      # navbar logo on every page
    "aboutedited.png",   # hero image on index.html
}

IMG_TAG_RE = re.compile(r'<img\b[^>]*>', re.IGNORECASE)
SRC_RE     = re.compile(r'\bsrc="([^"]+)"', re.IGNORECASE)
LOADING_RE = re.compile(r'\bloading="[^"]*"', re.IGNORECASE)

def filename(src):
    """Return just the filename from a src path."""
    return src.rsplit('/', 1)[-1].rsplit('\\', 1)[-1].lower()

def patch_img_tag(tag):
    """Add loading="lazy" to a single <img> tag if appropriate."""
    src_m = SRC_RE.search(tag)
    if not src_m:
        return tag, False

    img_src = src_m.group(1)
    fname   = filename(img_src)

    # Skip LCP images
    if fname in LCP_IMAGES:
        return tag, False

    # Skip if already has a loading attribute
    if LOADING_RE.search(tag):
        return tag, False

    # Insert loading="lazy" before the closing > or />
    if tag.rstrip().endswith('/>'):
        patched = tag.rstrip()[:-2].rstrip() + ' loading="lazy" />'
    else:
        patched = tag.rstrip()[:-1].rstrip() + ' loading="lazy">'

    return patched, True

def patch_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        src = f.read()

    total_added = 0

    def replacer(m):
        nonlocal total_added
        new_tag, changed = patch_img_tag(m.group(0))
        if changed:
            total_added += 1
        return new_tag

    result = IMG_TAG_RE.sub(replacer, src)

    if total_added > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(result)

    return total_added

# Collect all HTML files
html_files = (
    glob.glob('*.html') +
    glob.glob('services/*.html') +
    glob.glob('technology/*.html') +
    glob.glob('coe/*.html')
)

print()
print('═══════════════════════════════════════════')
print('  iGEN — add loading="lazy" to images')
print('═══════════════════════════════════════════')
print()

total_files  = 0
total_images = 0

for path in sorted(html_files):
    count = patch_file(path)
    if count > 0:
        print(f'  PATCHED  {path}  (+{count} lazy tags)')
        total_files  += 1
        total_images += count
    else:
        print(f'  OK       {path}')

print()
print('═══════════════════════════════════════════')
print(f'  Done.  {total_images} lazy tags added across {total_files} files.')
print('═══════════════════════════════════════════')
print()
print('Next: run convert-to-webp.py to convert images,')
print('then update HTML src paths to .webp.')
print()
