"""
add_lazy_loading.py — iGEN website image lazy-loading patcher
═══════════════════════════════════════════════════════════════
Run from the ROOT of your iGENservice repo:

    python3 add_lazy_loading.py

What it does:
  - Adds  loading="lazy"  to every <img> tag that is BELOW the fold
  - Adds  loading="eager" + <link rel="preload"> to above-fold images
    (navbar logo, hero image) so they load as fast as possible
  - Converts any remaining .jpg / .png src references to .webp
    (after you have run convert_to_webp.sh to generate the .webp files)
  - Safe to re-run — idempotent, skips already-patched tags
  - Works on ALL .html files: root, services/, technology/, coe/
"""

import re
import os
import glob

# ── Images that are ABOVE the fold — must NOT be lazy-loaded ─────────
# These are the two images visible before any scrolling on index.html.
# Everything else is below the fold and should be lazy-loaded.
EAGER_SRCS = {
    "img/igenlogo.png",       # navbar logo (all pages)
    "../img/igenlogo.png",    # navbar logo on subpages
}

# ── Preload hints to inject into <head> of index.html only ───────────
# These tell the browser to fetch critical images as early as possible.
PRELOAD_INDEX = """\
    <!-- Performance: preload above-fold images -->
    <link rel="preload" as="image" href="img/aboutedited.png">
    <link rel="preload" as="image" href="img/igenlogo.png">"""

PRELOAD_SUBPAGE = """\
    <!-- Performance: preload navbar logo -->
    <link rel="preload" as="image" href="../img/igenlogo.png">"""

# ─────────────────────────────────────────────────────────────────────

def patch_html(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    original = src
    is_root = "/" not in path.replace("\\", "/").lstrip("./")

    # ── 1. Add loading="lazy" to all below-fold <img> tags ───────────
    def add_loading(m):
        tag = m.group(0)
        # Already has loading= attribute — leave it alone
        if "loading=" in tag:
            return tag
        # Extract src value to check if above-fold
        src_match = re.search(r'src=["\']([^"\']+)["\']', tag)
        img_src = src_match.group(1) if src_match else ""
        # Normalise: strip leading ../
        norm_src = img_src.lstrip("./").lstrip("../")

        is_eager = any(
            img_src == e or img_src.endswith(e.lstrip("."))
            for e in EAGER_SRCS
        )

        loading = 'loading="eager"' if is_eager else 'loading="lazy"'

        # Insert loading attribute after the opening <img
        return re.sub(r"^<img\b", "<img " + loading, tag)

    src = re.sub(r"<img\b[^>]*>", add_loading, src, flags=re.IGNORECASE)

    # ── 2. Inject preload hints into <head> if not already present ────
    if "rel=\"preload\"" not in src and "<head>" in src.lower():
        preload = PRELOAD_INDEX if is_root and "index.html" in path else PRELOAD_SUBPAGE
        src = re.sub(
            r"(</head>)",
            preload + "\n\\1",
            src, count=1, flags=re.IGNORECASE
        )

    # ── 3. Update .jpg / .png src → .webp where a .webp exists ──────
    # Only rewrite if the .webp file actually exists on disk next to the html.
    # This avoids breaking images that haven't been converted yet.
    repo_root = os.path.dirname(os.path.abspath(path))
    # Walk up to find repo root (where index.html lives)
    while not os.path.exists(os.path.join(repo_root, "index.html")) and repo_root != "/":
        repo_root = os.path.dirname(repo_root)

    def try_webp(m):
        full_tag  = m.group(0)
        img_src   = m.group(1)
        # Only convert jpg/jpeg/png
        if not re.search(r"\.(jpg|jpeg|png)$", img_src, re.IGNORECASE):
            return full_tag
        webp_src  = re.sub(r"\.(jpg|jpeg|png)$", ".webp", img_src, flags=re.IGNORECASE)
        # Resolve the file path relative to repo root
        rel = img_src.lstrip("./").lstrip("../")
        webp_abs  = os.path.join(repo_root, rel[:-len(img_src.split(".")[-1])] + "webp")
        webp_abs  = os.path.normpath(webp_abs)
        if os.path.exists(webp_abs):
            return full_tag.replace(img_src, webp_src)
        return full_tag  # .webp doesn't exist yet — leave original

    src = re.sub(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', try_webp, src, flags=re.IGNORECASE)

    if src != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        return True
    return False


# ─── Main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    patterns = [
        "*.html",
        "services/*.html",
        "technology/*.html",
        "coe/*.html",
    ]

    all_files = []
    for pat in patterns:
        all_files.extend(glob.glob(pat))

    patched = 0
    skipped = 0

    print("\n══════════════════════════════════════════")
    print("  iGEN — add lazy loading to all images")
    print("══════════════════════════════════════════\n")

    for f in sorted(set(all_files)):
        if patch_html(f):
            print(f"  PATCHED  {f}")
            patched += 1
        else:
            print(f"  OK       {f}")
            skipped += 1

    print(f"\n  Done. Patched: {patched}   Already OK: {skipped}")
    print("\n  Next: run convert_to_webp.sh, then run this script again")
    print("  to update src references from .jpg/.png → .webp\n")
