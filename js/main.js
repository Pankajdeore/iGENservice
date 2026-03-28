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
