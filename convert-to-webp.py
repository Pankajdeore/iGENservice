"""
convert-to-webp.py  —  iGEN website image optimisation, Step 2
================================================================
Converts every .jpg / .jpeg / .png image used by the site to .webp,
then updates all <img> src attributes in the HTML to point to the
new .webp files.

Uses Python's built-in `subprocess` to call either:
  - cwebp  (Google's libwebp command-line tool)  — preferred
  - Pillow (Python library)                       — automatic fallback

INSTALL one of these first:
  Option A — cwebp (recommended, best quality):
    Mac:    brew install webp
    Linux:  sudo apt install webp
    Win:    choco install webp

  Option B — Pillow (pure Python, no extra install):
    pip install Pillow

Run from the ROOT of your iGENservice repo:
    python3 convert-to-webp.py

What it does:
  1. Scans img/, services-images/, technology-images/ for .jpg/.png files
  2. Converts each to a matching .webp file in the same folder
  3. Keeps originals — does NOT delete them (safe fallback)
  4. Updates all HTML <img src="..."> to reference the .webp version
  5. Wraps each converted <img> in a <picture> tag with WebP + original
     fallback, so older browsers still get the original format

Safe to re-run — skips images that already have a .webp version.
"""

import os
import re
import glob
import shutil
import subprocess
import sys

# ── Configuration ──────────────────────────────────────────────────
QUALITY     = 82     # WebP quality 0-100 (82 is a great balance)
IMAGE_DIRS  = ['img', 'services-images', 'technology-images']
EXTENSIONS  = {'.jpg', '.jpeg', '.png'}

# Images to SKIP converting (keep originals, e.g. already tiny)
SKIP_IMAGES = {'favicon.ico'}

# ── Detect conversion backend ───────────────────────────────────────
USE_CWEBP  = shutil.which('cwebp') is not None
USE_PILLOW = False
try:
    from PIL import Image
    USE_PILLOW = True
except ImportError:
    pass

if not USE_CWEBP and not USE_PILLOW:
    print()
    print('ERROR: No WebP conversion tool found.')
    print()
    print('Install one of:')
    print('  cwebp (Mac):   brew install webp')
    print('  cwebp (Linux): sudo apt install webp')
    print('  Pillow:        pip install Pillow')
    sys.exit(1)

backend = 'cwebp' if USE_CWEBP else 'Pillow'
print()
print('═══════════════════════════════════════════')
print(f'  iGEN — convert images to WebP  [{backend}]')
print('═══════════════════════════════════════════')
print()

# ── Step 1: Convert images ──────────────────────────────────────────
converted   = []
skipped     = []
errors      = []

for img_dir in IMAGE_DIRS:
    if not os.path.isdir(img_dir):
        print(f'  WARN  {img_dir}/ not found — skipping')
        continue

    for root, _, files in os.walk(img_dir):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in EXTENSIONS:
                continue
            if fname.lower() in SKIP_IMAGES:
                continue

            src_path  = os.path.join(root, fname)
            base_name = os.path.splitext(fname)[0]
            webp_path = os.path.join(root, base_name + '.webp')

            if os.path.exists(webp_path):
                skipped.append(src_path)
                print(f'  SKIP  {src_path}  (webp exists)')
                continue

            try:
                if USE_CWEBP:
                    result = subprocess.run(
                        ['cwebp', '-q', str(QUALITY), src_path, '-o', webp_path],
                        capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        raise RuntimeError(result.stderr.strip())
                else:
                    img = Image.open(src_path).convert('RGBA' if ext == '.png' else 'RGB')
                    img.save(webp_path, 'WEBP', quality=QUALITY)

                orig_kb = os.path.getsize(src_path) // 1024
                webp_kb = os.path.getsize(webp_path) // 1024
                saving  = round((1 - webp_kb / max(orig_kb, 1)) * 100)
                print(f'  CONV  {src_path}  {orig_kb}KB → {webp_kb}KB  (-{saving}%)')
                converted.append((src_path, webp_path))

            except Exception as e:
                print(f'  ERR   {src_path}  {e}')
                errors.append(src_path)

print()
print(f'  Converted: {len(converted)}   Skipped: {len(skipped)}   Errors: {len(errors)}')
print()

if not converted and not skipped:
    print('  No images found to convert. Check IMAGE_DIRS paths.')
    sys.exit(0)

# ── Step 2: Update HTML src paths + wrap in <picture> ───────────────
print('Updating HTML files...')
print()

# Build a mapping: original filename → webp filename (no path, just name)
webp_map = {}
for orig_path, webp_path in (converted + [(s, s.rsplit('.', 1)[0] + '.webp') for s in skipped]):
    orig_name = os.path.basename(orig_path)
    webp_name = os.path.basename(webp_path)
    webp_map[orig_name.lower()] = (orig_name, webp_name)

IMG_TAG_RE = re.compile(r'<img\b[^>]+>', re.IGNORECASE)
SRC_RE     = re.compile(r'\bsrc="([^"]+)"', re.IGNORECASE)

def upgrade_img_tag(tag):
    """
    Convert an <img src="foo.jpg"> to:
    <picture>
      <source srcset="foo.webp" type="image/webp">
      <img src="foo.jpg" ...>
    </picture>

    Returns the original tag unchanged if:
    - src doesn't point to a converted image
    - the img is already inside a <picture>
    """
    src_m = SRC_RE.search(tag)
    if not src_m:
        return tag

    img_src  = src_m.group(1)
    orig_fname = img_src.rsplit('/', 1)[-1]

    entry = webp_map.get(orig_fname.lower())
    if not entry:
        return tag  # not a converted image

    orig_name, webp_name = entry
    webp_src = img_src.rsplit('/', 1)[0] + '/' + webp_name if '/' in img_src else webp_name

    picture = (
        f'<picture>\n'
        f'  <source srcset="{webp_src}" type="image/webp">\n'
        f'  {tag}\n'
        f'</picture>'
    )
    return picture

html_files = (
    glob.glob('*.html') +
    glob.glob('services/*.html') +
    glob.glob('technology/*.html') +
    glob.glob('coe/*.html')
)

html_updated = 0

for path in sorted(html_files):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        src = f.read()

    # Skip if already wrapped (simple check to avoid double-wrapping)
    original = src

    # Don't process img tags already inside <picture>
    # We do this by replacing outside-picture img tags only
    def replacer(m):
        # Check a few chars before the match for <picture
        start = max(0, m.start() - 50)
        context = src[start:m.start()]
        if '<picture' in context.lower():
            return m.group(0)  # already in a picture element
        return upgrade_img_tag(m.group(0))

    result = IMG_TAG_RE.sub(replacer, src)

    if result != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'  UPDATED  {path}')
        html_updated += 1

print()
print('═══════════════════════════════════════════')
print(f'  Done.  {len(converted)} images converted.')
print(f'         {html_updated} HTML files updated.')
print('═══════════════════════════════════════════')
print()
print('Originals kept — delete them once you have verified the site.')
print()
print('Next steps:')
print('  git add img/ services-images/ technology-images/ *.html')
print('  git add services/*.html technology/*.html coe/*.html')
print('  git commit -m "Convert images to WebP, add lazy loading"')
print('  git push')
print()
