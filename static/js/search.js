document.addEventListener("DOMContentLoaded", () => {
    const inputs = document.querySelectorAll("[data-search-input]");
    const suggestUrl = "/products/suggest/";

    inputs.forEach((input) => {
        const wrapper = input.closest("[data-search-wrapper]");
        const dropdown = wrapper ? wrapper.querySelector("[data-search-dropdown]") : null;

        if (!wrapper || !dropdown) {
            return;
        }

        let activeIndex = -1;
        let debounceTimer = null;
        let suggestions = [];

        const hideDropdown = () => {
            dropdown.classList.add("hidden");
            dropdown.innerHTML = "";
            input.setAttribute("aria-expanded", "false");
            activeIndex = -1;
            suggestions = [];
        };

        const renderDropdown = (items) => {
            if (!items.length) {
                hideDropdown();
                return;
            }

            dropdown.innerHTML = items
                .map(
                    (item, index) => `
                    <a href="/products/${item.slug}/"
                       class="search-suggest-item block px-4 py-3 hover:bg-cream transition-colors"
                       data-suggest-index="${index}"
                       role="option">
                        <span class="text-brown font-medium">${item.name}</span>
                        <span class="text-gold text-sm ml-2">₹${item.price}</span>
                    </a>`
                )
                .join("");

            dropdown.classList.remove("hidden");
            input.setAttribute("aria-expanded", "true");
        };

        const fetchSuggestions = (query) => {
            if (query.length < 2) {
                hideDropdown();
                return;
            }

            fetch(`${suggestUrl}?q=${encodeURIComponent(query)}`)
                .then((response) => response.json())
                .then((data) => {
                    suggestions = data;
                    renderDropdown(data);
                })
                .catch(() => hideDropdown());
        };

        input.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetchSuggestions(input.value.trim());
            }, 250);
        });

        input.addEventListener("keydown", (event) => {
            const items = dropdown.querySelectorAll("[data-suggest-index]");

            if (!items.length) {
                return;
            }

            if (event.key === "ArrowDown") {
                event.preventDefault();
                activeIndex = Math.min(activeIndex + 1, items.length - 1);
                items[activeIndex].focus();
            } else if (event.key === "ArrowUp") {
                event.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                items[activeIndex].focus();
            } else if (event.key === "Escape") {
                hideDropdown();
            }
        });

        document.addEventListener("click", (event) => {
            if (!wrapper.contains(event.target)) {
                hideDropdown();
            }
        });
    });
});
