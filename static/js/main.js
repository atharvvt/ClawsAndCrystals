document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("mobile-menu-toggle");
    var nav = document.getElementById("mobile-nav");
    var focusableSelector = "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])";

    if (toggle && nav) {
        var previousFocus = null;

        var trapFocus = function (event) {
            if (!nav.classList.contains("is-open") || event.key !== "Tab") {
                return;
            }

            var focusable = Array.prototype.slice.call(nav.querySelectorAll(focusableSelector));
            if (!focusable.length) {
                return;
            }

            var first = focusable[0];
            var last = focusable[focusable.length - 1];

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        };

        toggle.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
            toggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");

            if (isOpen) {
                previousFocus = document.activeElement;
                var firstFocusable = nav.querySelector(focusableSelector);
                if (firstFocusable) {
                    firstFocusable.focus();
                }
                document.addEventListener("keydown", trapFocus);
            } else {
                document.removeEventListener("keydown", trapFocus);
                if (previousFocus) {
                    previousFocus.focus();
                }
            }
        });
    }

    document.querySelectorAll("[data-dismiss-alert]").forEach(function (button) {
        button.addEventListener("click", function () {
            var alert = button.closest(".alert");
            if (alert) {
                alert.remove();
            }
        });
    });

    window.addEventListener("pageshow", function (event) {
        if (event.persisted && document.querySelector("form[method='post'] input[name='csrfmiddlewaretoken']")) {
            window.location.reload();
        }
    });
});
