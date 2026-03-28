/*
 * main.js — iGEN website
 * Requires: jQuery 3.x, Bootstrap 4, OwlCarousel 2
 * All lib/ dependencies replaced with CDN — see script tags in each HTML file.
 */

(function ($) {
    "use strict";

    /* ── Dynamic copyright year ─────────────────────────────────── */
    var yrEl = document.getElementById("yr");
    if (yrEl) yrEl.textContent = new Date().getFullYear();

    /* ── Auto active nav link ────────────────────────────────────── */
    /*
     * Removes ALL hard-coded 'active' classes from nav links,
     * then adds it only to the link that matches the current page.
     * Handles root pages (index.html, about.html, contact.html).
     */
    var currentPage = window.location.pathname.split("/").pop() || "index.html";
    $(".navbar-nav .nav-link").removeClass("active");
    $(".navbar-nav .nav-link").each(function () {
        var href = $(this).attr("href");
        if (href && href.split("/").pop() === currentPage) {
            $(this).addClass("active");
        }
    });

    /* ── Back to Top button ──────────────────────────────────────── */
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $(".back-to-top").fadeIn("slow");
        } else {
            $(".back-to-top").fadeOut("slow");
        }
    });

    $(".back-to-top").click(function () {
        $("html, body").animate({ scrollTop: 0 }, 1200, "swing");
        return false;
    });

    /* ── Team Owl Carousel ───────────────────────────────────────── */
    if ($(".team-carousel").length) {
        $(".team-carousel").owlCarousel({
            autoplay: true,
            autoplayTimeout: 4000,
            smartSpeed: 800,
            margin: 25,
            loop: true,
            nav: true,
            navText: [
                '<i class="fa fa-chevron-left"></i>',
                '<i class="fa fa-chevron-right"></i>',
            ],
            dots: true,
            responsive: {
                0: { items: 1 },
                576: { items: 1 },
                768: { items: 2 },
                992: { items: 3 },
            },
        });
    }

    /* ── Cookie / Privacy banner ─────────────────────────────────── */
    /*
     * Shows a GDPR/CCPA cookie notice on first visit.
     * Stored in localStorage so it only appears once.
     */
    if (!localStorage.getItem("igenCookieAccepted")) {
        var banner = document.getElementById("cookie-banner");
        if (banner) banner.style.display = "flex";
    }

    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "cookie-accept") {
            localStorage.setItem("igenCookieAccepted", "1");
            var banner = document.getElementById("cookie-banner");
            if (banner) banner.style.display = "none";
        }
    });

})(jQuery);

/* ── Scroll Reveal — IntersectionObserver ───────────────────────────
 *
 * Runs outside the jQuery wrapper so it fires immediately on DOMContentLoaded
 * and does not depend on jQuery being ready.
 *
 * Logic:
 *  - Finds every element with class .reveal on the page.
 *  - Watches each one with IntersectionObserver (threshold: 15% visible).
 *  - Adds .revealed when the element crosses the threshold.
 *  - Unobserves immediately after — animation plays once and stays put.
 *  - Falls back gracefully: if IntersectionObserver is not supported
 *    (very old browsers), all .reveal elements are made visible immediately.
 * ─────────────────────────────────────────────────────────────────── */
(function () {
    var revealEls = document.querySelectorAll(".reveal");

    /* Graceful fallback for browsers without IntersectionObserver */
    if (!("IntersectionObserver" in window)) {
        revealEls.forEach(function (el) {
            el.classList.add("revealed");
        });
        return;
    }

    var observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed");
                    observer.unobserve(entry.target); /* fire once only */
                }
            });
        },
        {
            threshold: 0.15,   /* trigger when 15% of element is visible */
            rootMargin: "0px 0px -40px 0px" /* slight bottom offset — feels more intentional */
        }
    );

    revealEls.forEach(function (el) {
        observer.observe(el);
    });
})();

/* ── Sticky shrinking navbar ─────────────────────────────────────────
 *
 * Runs as a standalone IIFE — no jQuery dependency.
 *
 * On scroll:
 *  1. Measures the navbar's natural height once on load.
 *  2. Injects a #nav-placeholder <div> of the same height so the page
 *     doesn't jump when #mainNav becomes position:fixed.
 *  3. Toggles .nav-sticky on #mainNav based on scrollY vs navHeight.
 *  4. Updates the #nav-progress bar width as a percentage of total
 *     scrollable page height (nice bonus UX touch).
 * ─────────────────────────────────────────────────────────────────── */
(function () {
    var nav = document.getElementById("mainNav");
    if (!nav) return;

    /* Inject a progress bar element inside the navbar */
    var progressBar = document.createElement("div");
    progressBar.id = "nav-progress";
    nav.appendChild(progressBar);

    /* Inject a placeholder that fills the gap when nav goes fixed */
    var placeholder = document.createElement("div");
    placeholder.id = "nav-placeholder";
    nav.parentNode.insertBefore(placeholder, nav.nextSibling);

    var navHeight = nav.offsetHeight;
    placeholder.style.height = "0px";        /* starts at 0 — only used when sticky */
    var isSticky = false;

    function onScroll() {
        var scrollY      = window.pageYOffset || document.documentElement.scrollTop;
        var docHeight    = document.documentElement.scrollHeight - window.innerHeight;
        var scrollPct    = docHeight > 0 ? (scrollY / docHeight) * 100 : 0;

        /* Update scroll progress bar */
        progressBar.style.width = Math.min(scrollPct, 100).toFixed(1) + "%";

        /* Toggle sticky class */
        if (scrollY > navHeight && !isSticky) {
            nav.classList.add("nav-sticky");
            placeholder.style.height = navHeight + "px";  /* prevent jump */
            isSticky = true;
        } else if (scrollY <= navHeight && isSticky) {
            nav.classList.remove("nav-sticky");
            placeholder.style.height = "0px";
            isSticky = false;
        }
    }

    /* Recalculate navHeight if window is resized */
    window.addEventListener("resize", function () {
        if (!isSticky) navHeight = nav.offsetHeight;
    });

    window.addEventListener("scroll", onScroll, { passive: true });

    /* Run once on load in case page is refreshed mid-scroll */
    onScroll();
})();
