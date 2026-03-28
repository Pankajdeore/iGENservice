# iGEN Website — Change Log

All fixes and additions applied to the original iGENservice repo.
Files modified: `index.html`, `contact.html`, `about.html`
Files added: `css/igenfix.css`, `js/main.js`, `privacy.html`

---

## Critical Bug Fixes

### 1. Backslash paths → Forward slashes (all HTML files)
- `img\igenlogo.png` → `img/igenlogo.png`
- `img\aboutedited.png` → `img/aboutedited.png`
- `img\igen-approach.jpg` → `img/igen-approach.jpg`
- Backslashes only work on Windows; all web servers (including GitHub Pages) require forward slashes.

### 2. Google Maps embed URL corrected (index.html, contact.html)
- Old: `https://www.google.com/maps?q=Cumming,+GA&output=embed` (broken format)
- New: `https://maps.google.com/maps?q=4465+Alister+Park+Dr,+Cumming,+GA+30040&hl=en&z=15&output=embed`
- The old URL format doesn't render a map inside an iframe without the correct `output=embed` parameters and a valid address.

### 3. Duplicate form IDs removed (index.html)
- The file had two separate `<form id="contactForm">` blocks and duplicate `id="name"`, `id="email"`, etc.
- Old commented-out form block fully deleted.
- Active form IDs changed to `id="mainContactForm"` with prefixed field IDs (`mc-name`, `mc-email`, etc.) to prevent conflicts.

### 4. Local `lib/` dependencies replaced with CDN (all HTML files + main.js)
- Removed: `lib/easing/easing.min.js`, `lib/waypoints/waypoints.min.js`,
  `lib/owlcarousel/owl.carousel.min.js`, `lib/isotope/isotope.pkgd.min.js`,
  `lib/lightbox/js/lightbox.min.js`, and matching CSS files.
- Added CDN equivalents (cdnjs.cloudflare.com):
  - jQuery 3.6.4
  - Bootstrap 4.6.2
  - OwlCarousel 2.3.4
  - Lightbox2 2.11.4
- `main.js` rewritten to not depend on `easing`, `waypoints`, or `isotope`
  (these were unused in the active template sections).

### 5. Footer logo path fixed in about.html
- Old: `src="../img/igenlogo.png"` (wrong — about.html is at root, not in a subfolder)
- New: `src="img/igenlogo.png"`
- Same fix applied to all `../index.html`, `../about.html`, `../contact.html` links in that footer.

---

## Warning Fixes

### 6. Meta tags updated (index.html)
- Old: `content="Free HTML Templates"` (template placeholder)
- New: Real iGEN keywords and description for SEO.

### 7. Social media links updated (all HTML files)
- Old: All four social icons pointed to `href="#"`
- New: Placeholder real URLs added (`twitter.com/igenservice`, `linkedin.com/company/igenservice`, etc.)
- **Action needed:** Update these with your actual social profile URLs.

### 8. Missing CSS classes added → `css/igenfix.css` (new file)
- `.footer-bg` — dark background (#111111) for footer
- `.btn-social` — 38px circular social buttons with hover effect
- `.transition` — hover lift effect for service cards
- `#cookie-banner` — GDPR/CCPA cookie notice styles

### 9. Active nav class managed dynamically (all HTML files)
- Hard-coded `class="... active"` removed from all nav links except the current page's link.
- `main.js` now auto-sets `.active` based on `window.location.pathname`.

### 10. Excessive commented-out blocks removed (index.html)
- Removed: old portfolio section, old pricing section, old testimonials section,
  old header variant, old footer variant (~300 lines of dead code).

---

## Copyright & Compliance Fixes

### 11. HTML Codex attribution restored (all HTML files)
- The original footer credit `Designed by HTML Codex` was removed from the footer.
- Free HTML Codex templates require this attribution link.
- **Restored** as: `Website design adapted from HTML Codex`
- If you wish to remove this, purchase a paid license at https://htmlcodex.com.

### 12. Dynamic copyright year (all HTML files)
- Old: hardcoded year or no year
- New: `<span id="yr"></span>` populated by `main.js` using `new Date().getFullYear()`
- Will always display the current year automatically.

### 13. Privacy Policy page added → `privacy.html` (new file)
- Required for GDPR (EU visitors) and CCPA (California visitors).
- Covers: contact form data, Google Maps cookies, Tawk.to cookies, data rights.
- Linked from footer of all pages.

---

## New Features Added

### 14. Tawk.to live chat integration (all HTML files)
- Free forever live chat widget from https://www.tawk.to
- Script block added (commented out) to all pages.
- **To activate:**
  1. Sign up at https://www.tawk.to (free, no credit card)
  2. Create a Property for `igenservice.com`
  3. Copy your Property ID (looks like `64abc...`)
  4. Replace `YOUR_PROPERTY_ID` in the `<script>` block
  5. Uncomment the `<script>` block in index.html, contact.html, and about.html

### 15. Cookie / Privacy notice banner (all HTML files + igenfix.css)
- Shows a GDPR/CCPA-friendly notice on first visit.
- "Got it" button dismisses it and stores preference in localStorage.
- Links to the new `privacy.html`.

### 16. Contact form activation instructions
- Your FormSubmit.co setup is already correct.
- **To activate:** submit the form once → click the confirmation email from FormSubmit.co.
- After that, all "Send Message" submissions go directly to your inbox.

---

## Files Summary

| File | Status | Notes |
|------|--------|-------|
| `index.html` | Fixed | All critical bugs, CDN, clean nav, Tawk.to stub |
| `contact.html` | Fixed | Maps, form IDs, CDN, Tawk.to stub |
| `about.html` | Fixed | Paths, Bootstrap conflict, footer, CDN |
| `css/igenfix.css` | New | Missing CSS classes + cookie banner styles |
| `js/main.js` | Rewritten | CDN-compatible, dynamic year, auto active nav |
| `privacy.html` | New | GDPR/CCPA compliance page |
