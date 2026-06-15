document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("mobile-menu-toggle");
    var nav = document.getElementById("mobile-nav");

    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
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
});
