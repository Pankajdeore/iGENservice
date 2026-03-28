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
