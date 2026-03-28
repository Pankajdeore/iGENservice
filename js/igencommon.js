/*
 * igencommon.js — iGEN universal subpage fix script
 * ─────────────────────────────────────────────────
 * Drop this into js/ and add ONE script tag to every HTML file in
 * services/, technology/, coe/ (and any future subfolders):
 *
 *   <script src="../js/igencommon.js"></script>
 *
 * Works on root-level pages too (index.html, about.html, etc.) —
 * it auto-detects depth and adjusts all asset paths accordingly.
 *
 * What this script does (in order):
 *  1. Detects subfolder depth → sets correct base path for assets
 *  2. Applies saved dark mode class to <body> BEFORE first paint (no flash)
 *  3. Injects igenfix.css link into <head> if not already present
 *  4. On DOMContentLoaded:
 *     a. Adds id="mainNav" + nav-logo class to navbar elements
 *     b. Injects dark mode toggle buttons (desktop + mobile)
 *     c. Injects cookie banner
 *     d. Injects back-to-top button
 *     e. Fixes footer: dynamic year, copyright link, privacy link, attribution
 *     f. Auto-sets active nav link for current page
 *     g. Initialises sticky shrinking navbar + scroll progress bar
 *     h. Initialises scroll reveal (IntersectionObserver)
 *     i. Initialises OwlCarousel team section (if present)
 *     j. Wires dark mode toggles with localStorage persistence
 *     k. Wires cookie banner acceptance
 *     l. Wires back-to-top button
 */

(function () {
    "use strict";

    /* ══════════════════════════════════════════════════════════════
     * 1. BASE PATH DETECTION
     * Works out whether this page is at root or in a subfolder.
     * Root: /index.html, /about.html → base = ""
     * Sub:  /services/digital.html  → base = "../"
     * ══════════════════════════════════════════════════════════════ */
    var pathParts = window.location.pathname.replace(/^\//, "").split("/").filter(Boolean);
    var isSubfolder = pathParts.length > 1;
    var base = isSubfolder ? "../" : "";

    /* ══════════════════════════════════════════════════════════════
     * 2. DARK MODE — apply BEFORE first paint to avoid flash
     * ══════════════════════════════════════════════════════════════ */
    var storedTheme = localStorage.getItem("igenDarkMode");
    if (storedTheme === null) {
        storedTheme = (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)
            ? "dark" : "light";
    }
    if (storedTheme === "dark") {
        document.body.classList.add("dark-mode");
    }

    /* ══════════════════════════════════════════════════════════════
     * 3. INJECT igenfix.css if not already in <head>
     * ══════════════════════════════════════════════════════════════ */
    var cssHref = base + "css/igenfix.css";
    var alreadyLoaded = false;
    var links = document.querySelectorAll("link[rel='stylesheet']");
    for (var i = 0; i < links.length; i++) {
        if (links[i].getAttribute("href") && links[i].getAttribute("href").indexOf("igenfix") !== -1) {
            alreadyLoaded = true;
            break;
        }
    }
    if (!alreadyLoaded) {
        var cssLink = document.createElement("link");
        cssLink.rel = "stylesheet";
        cssLink.href = cssHref;
        document.head.appendChild(cssLink);
    }

    /* ══════════════════════════════════════════════════════════════
     * HELPERS
     * ══════════════════════════════════════════════════════════════ */

    /** Build the shared navbar HTML string (used for injection check only) */
    function buildToggleBtn(id, extraClass) {
        return '<button id="' + id + '" class="dm-toggle' + (extraClass ? " " + extraClass : "") +
            '" aria-label="Toggle dark mode" title="Toggle dark mode">' +
            '<i class="fa fa-moon"></i></button>';
    }

    /** Sync moon/sun icon on all dm-toggle buttons */
    function syncIcons(dark) {
        document.querySelectorAll(".dm-toggle").forEach(function (btn) {
            var icon = btn.querySelector(".fa");
            if (!icon) return;
            icon.className = dark ? "fa fa-sun" : "fa fa-moon";
        });
    }

    /** Apply dark mode class + save preference */
    function applyDark(dark) {
        if (dark) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("igenDarkMode", "dark");
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("igenDarkMode", "light");
        }
        syncIcons(dark);
    }

    /* ══════════════════════════════════════════════════════════════
     * DOM READY
     * ══════════════════════════════════════════════════════════════ */
    document.addEventListener("DOMContentLoaded", function () {

        /* ── a. NAVBAR: add id + class if missing ──────────────────── */
        var navWrapper = document.querySelector(".container-fluid.bg-white.position-relative");
        if (navWrapper && !navWrapper.id) {
            navWrapper.id = "mainNav";
        }
        var logoImg = document.querySelector(".navbar-brand img");
        if (logoImg && !logoImg.classList.contains("nav-logo")) {
            logoImg.classList.add("nav-logo");
        }

        /* ── b. DARK MODE TOGGLE BUTTONS — inject if not present ────── */
        if (!document.getElementById("darkToggle")) {
            /* Desktop toggle — goes inside the d-none d-lg-flex area */
            var desktopArea = document.querySelector(".d-none.d-lg-flex");
            if (desktopArea) {
                var dtBtn = document.createElement("button");
                dtBtn.id = "darkToggle";
                dtBtn.className = "dm-toggle mr-3";
                dtBtn.setAttribute("aria-label", "Toggle dark mode");
                dtBtn.setAttribute("title", "Toggle dark mode");
                dtBtn.innerHTML = '<i class="fa fa-moon"></i>';
                desktopArea.insertBefore(dtBtn, desktopArea.firstChild);
            }
        }
        if (!document.getElementById("darkToggleMobile")) {
            /* Mobile toggle — goes right before the hamburger button */
            var toggler = document.querySelector("button.navbar-toggler");
            if (toggler) {
                var mbBtn = document.createElement("button");
                mbBtn.id = "darkToggleMobile";
                mbBtn.className = "dm-toggle d-lg-none";
                mbBtn.setAttribute("aria-label", "Toggle dark mode");
                mbBtn.setAttribute("title", "Toggle dark mode");
                mbBtn.innerHTML = '<i class="fa fa-moon"></i>';
                toggler.parentNode.insertBefore(mbBtn, toggler);
            }
        }
        /* Set correct icon for current mode */
        syncIcons(document.body.classList.contains("dark-mode"));

        /* Wire toggle clicks */
        document.querySelectorAll(".dm-toggle").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var nowDark = !document.body.classList.contains("dark-mode");
                btn.classList.add("spinning");
                setTimeout(function () { btn.classList.remove("spinning"); }, 400);
                applyDark(nowDark);
            });
        });

        /* ── c. COOKIE BANNER — inject if not present ───────────────── */
        if (!document.getElementById("cookie-banner")) {
            var banner = document.createElement("div");
            banner.id = "cookie-banner";
            banner.style.display = "none";
            banner.innerHTML =
                '<span>This site uses cookies to enhance your experience. ' +
                'See our <a href="' + base + 'privacy.html">Privacy Policy</a>.</span>' +
                '<button id="cookie-accept">Got it</button>';
            document.body.appendChild(banner);
            if (!localStorage.getItem("igenCookieAccepted")) {
                banner.style.display = "flex";
            }
        }
        document.addEventListener("click", function (e) {
            if (e.target && e.target.id === "cookie-accept") {
                localStorage.setItem("igenCookieAccepted", "1");
                var b = document.getElementById("cookie-banner");
                if (b) b.style.display = "none";
            }
        });

        /* ── d. BACK-TO-TOP button — inject if not present ─────────── */
        if (!document.querySelector(".back-to-top")) {
            var btt = document.createElement("a");
            btt.href = "#";
            btt.className = "btn btn-lg btn-primary btn-lg-square back-to-top";
            btt.innerHTML = '<i class="fa fa-angle-up"></i>';
            document.body.appendChild(btt);
        }
        window.addEventListener("scroll", function () {
            var bttEl = document.querySelector(".back-to-top");
            if (!bttEl) return;
            bttEl.style.display = (window.pageYOffset > 300) ? "flex" : "none";
        }, { passive: true });
        document.addEventListener("click", function (e) {
            if (e.target && e.target.closest(".back-to-top")) {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });

        /* ── e. FOOTER FIXES ─────────────────────────────────────────
         *  - Dynamic year via <span id="yr">
         *  - Fix © link from "#" → correct index.html path
         *  - Add Privacy Policy link if missing
         *  - Add HTML Codex attribution if missing (license compliance)
         * ─────────────────────────────────────────────────────────── */
        var yr = document.getElementById("yr");
        if (yr) {
            yr.textContent = new Date().getFullYear();
        }

        /* Fix copyright year span if it's missing entirely */
        var footerText = document.querySelector(".footer-bg .col-12.text-center");
        if (footerText) {
            var html = footerText.innerHTML;

            /* Inject year span if not present */
            if (html.indexOf('id="yr"') === -1) {
                /* Replace bare © text with a year span */
                var year = new Date().getFullYear();
                footerText.querySelectorAll("p").forEach(function (p) {
                    if (p.innerHTML.indexOf("&copy;") !== -1 || p.innerHTML.indexOf("©") !== -1) {
                        /* Fix the copyright link from "#" to actual index path */
                        p.innerHTML = p.innerHTML
                            .replace(/href="#"/, 'href="' + base + 'index.html"')
                            .replace(/©\s*<a/, '© <span id="yr">' + year + '</span> <a');
                    }
                });
            }

            /* Add Privacy Policy link if quick-links column exists but privacy missing */
            var quickLinks = document.querySelector(".col-lg-3 .d-flex.flex-column");
            if (quickLinks && quickLinks.innerHTML.indexOf("privacy") === -1) {
                var privLi = document.createElement("a");
                privLi.className = "text-white-50";
                privLi.href = base + "privacy.html";
                privLi.innerHTML = '<i class="fa fa-angle-right text-primary mr-2"></i>Privacy Policy';
                quickLinks.appendChild(privLi);
            }

            /* Add HTML Codex attribution if missing */
            var hasCodex = footerText.innerHTML.indexOf("htmlcodex") !== -1 ||
                           footerText.innerHTML.indexOf("HTML Codex") !== -1;
            if (!hasCodex) {
                var attr = document.createElement("p");
                attr.className = "mb-0 text-white-50";
                attr.style.fontSize = "0.85rem";
                attr.innerHTML = 'Website design adapted from ' +
                    '<a href="https://htmlcodex.com" class="text-white-50" ' +
                    'target="_blank" rel="noopener">HTML Codex</a>';
                footerText.appendChild(attr);
            }
        }

        /* Fix COE pages where footer logo href points to coe/index.html */
        var footerBrand = document.querySelector(".footer-bg .navbar-brand");
        if (footerBrand) {
            var brandHref = footerBrand.getAttribute("href");
            if (brandHref && brandHref.indexOf("coe/index.html") !== -1) {
                footerBrand.href = base + "index.html";
            }
        }

        /* Fix footer logo img path — ensure it uses the correct base */
        var footerLogo = document.querySelector(".footer-bg img");
        if (footerLogo) {
            var src = footerLogo.getAttribute("src") || "";
            /* If it's a root-relative path like /img/igenlogo.png already fine;
               if it's a broken relative like igenlogo.png fix it */
            if (!src.startsWith("http") && !src.startsWith("/") && src.indexOf("igenlogo") !== -1) {
                if (isSubfolder && src.indexOf("../") === -1) {
                    footerLogo.src = base + "img/igenlogo.png";
                }
            }
        }

        /* ── f. ACTIVE NAV LINK ──────────────────────────────────────── */
        var currentFile = window.location.pathname.split("/").pop() || "index.html";
        document.querySelectorAll(".navbar-nav .nav-link").forEach(function (link) {
            link.classList.remove("active");
            var href = link.getAttribute("href") || "";
            if (href.split("/").pop() === currentFile) {
                link.classList.add("active");
            }
        });

        /* ── g. STICKY SHRINKING NAVBAR ─────────────────────────────── */
        var nav = document.getElementById("mainNav");
        if (nav) {
            /* Inject scroll progress bar */
            if (!document.getElementById("nav-progress")) {
                var pb = document.createElement("div");
                pb.id = "nav-progress";
                nav.appendChild(pb);
            }
            /* Inject placeholder to prevent jump */
            var placeholder = document.getElementById("nav-placeholder");
            if (!placeholder) {
                placeholder = document.createElement("div");
                placeholder.id = "nav-placeholder";
                nav.parentNode.insertBefore(placeholder, nav.nextSibling);
            }
            var navH = nav.offsetHeight;
            var sticky = false;
            function onScroll() {
                var sy = window.pageYOffset || 0;
                var dh = document.documentElement.scrollHeight - window.innerHeight;
                var pb2 = document.getElementById("nav-progress");
                if (pb2) pb2.style.width = (dh > 0 ? Math.min(sy / dh * 100, 100) : 0).toFixed(1) + "%";
                if (sy > navH && !sticky) {
                    nav.classList.add("nav-sticky");
                    placeholder.style.height = navH + "px";
                    sticky = true;
                } else if (sy <= navH && sticky) {
                    nav.classList.remove("nav-sticky");
                    placeholder.style.height = "0px";
                    sticky = false;
                }
            }
            window.addEventListener("resize", function () { if (!sticky) navH = nav.offsetHeight; });
            window.addEventListener("scroll", onScroll, { passive: true });
            onScroll();
        }

        /* ── h. SCROLL REVEAL ────────────────────────────────────────── */
        var revealEls = document.querySelectorAll(".reveal");
        if (revealEls.length > 0) {
            if (!("IntersectionObserver" in window)) {
                revealEls.forEach(function (el) { el.classList.add("revealed"); });
            } else {
                var observer = new IntersectionObserver(function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            entry.target.classList.add("revealed");
                            observer.unobserve(entry.target);
                        }
                    });
                }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
                revealEls.forEach(function (el) { observer.observe(el); });
            }
        }

        /* ── i. OWL CAROUSEL (team section) ─────────────────────────── */
        if (typeof jQuery !== "undefined" && typeof jQuery.fn.owlCarousel !== "undefined") {
            var $carousel = jQuery(".team-carousel");
            if ($carousel.length && !$carousel.hasClass("owl-loaded")) {
                $carousel.owlCarousel({
                    autoplay: true, autoplayTimeout: 4000, smartSpeed: 800,
                    margin: 25, loop: true, nav: true, dots: true,
                    navText: ['<i class="fa fa-chevron-left"></i>', '<i class="fa fa-chevron-right"></i>'],
                    responsive: { 0: { items: 1 }, 768: { items: 2 }, 992: { items: 3 } }
                });
            }
        }

        /* ── j. GREY SECTION TAGGING for dark mode CSS hook ────────── */
        document.querySelectorAll('[style*="background: #f8f9fa"], [style*="background:#f8f9fa"]')
            .forEach(function (el) { el.classList.add("dm-section"); });

        /* ── k. COOKIE BANNER — show if not yet accepted ────────────── */
        if (!localStorage.getItem("igenCookieAccepted")) {
            var cb = document.getElementById("cookie-banner");
            if (cb) cb.style.display = "flex";
        }

        /* ── l. EMAIL FIX ──────────────────────────────────────────────
         *
         * TWO problems solved here:
         *
         * Problem 1 — Cloudflare Email Obfuscation
         *   Cloudflare replaces plain email addresses in HTML with an
         *   encoded anchor: <a href="/cdn-cgi/l/email-protection"
         *   class="__cf_email__" data-cfemail="HEX">[email protected]</a>
         *   This decoder reverses the XOR encoding and restores the
         *   original email text and mailto: href.
         *
         *   Algorithm: first byte of hex = XOR key.
         *   Each subsequent byte pair XORed with key = character code.
         *
         * Problem 2 — CF-proof email spans (data-u + data-d attributes)
         *   The patch script replaces plain email text in HTML with:
         *   <span class="ig-email" data-u="org" data-d="igenservice.com"></span>
         *   Cloudflare cannot detect email addresses in data attributes,
         *   so these pass through untouched. This function assembles them.
         *
         * NOTE: The permanent fix is to disable Email Obfuscation in the
         * Cloudflare dashboard: Websites → your domain → Scrape Shield
         * → Email Address Obfuscation → OFF.
         * ─────────────────────────────────────────────────────────────── */

        /* Decode a Cloudflare-encoded email hex string */
        function decodeCFEmail(hex) {
            var key = parseInt(hex.slice(0, 2), 16);
            var email = '';
            for (var i = 2; i < hex.length; i += 2) {
                email += String.fromCharCode(parseInt(hex.slice(i, i + 2), 16) ^ key);
            }
            return email;
        }

        /* Fix 1: Restore all Cloudflare-obfuscated email anchors */
        document.querySelectorAll('a.__cf_email__[data-cfemail]').forEach(function (el) {
            var encoded = el.getAttribute('data-cfemail');
            if (!encoded) return;
            var email = decodeCFEmail(encoded);
            el.textContent = email;
            el.href = 'mailto:' + email;
            el.removeAttribute('data-cfemail');
            el.classList.remove('__cf_email__');
        });

        /* Fix 2: Build emails from CF-proof data-u / data-d span attributes */
        document.querySelectorAll('span.ig-email[data-u][data-d]').forEach(function (el) {
            var user   = el.getAttribute('data-u');
            var domain = el.getAttribute('data-d');
            var email  = user + '@' + domain;
            /* Replace the span with a proper mailto anchor */
            var a = document.createElement('a');
            a.href = 'mailto:' + email;
            a.textContent = email;
            a.className = el.className.replace('ig-email', '').trim();
            el.parentNode.replaceChild(a, el);
        });

    }); /* end DOMContentLoaded */

})();
