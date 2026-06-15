document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("quick-view-modal");
    const modalBody = document.getElementById("quick-view-body");
    const closeBtn = document.getElementById("quick-view-close");

    if (!modal || !modalBody) {
        return;
    }

    const closeModal = () => {
        modal.classList.add("hidden");
        modal.setAttribute("aria-hidden", "true");
        modalBody.innerHTML = "";
        document.body.classList.remove("overflow-hidden");
    };

    const openModal = async (slug) => {
        modal.classList.remove("hidden");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("overflow-hidden");
        modalBody.innerHTML = '<p class="text-muted p-8 text-center">Loading...</p>';

        try {
            const response = await fetch(`/products/${slug}/quick-view/`);
            if (!response.ok) {
                throw new Error("Failed to load");
            }
            modalBody.innerHTML = await response.text();
        } catch (error) {
            modalBody.innerHTML = '<p class="text-red-500 p-8 text-center">Could not load product.</p>';
        }
    };

    document.addEventListener("click", (event) => {
        const trigger = event.target.closest("[data-quick-view]");
        if (!trigger) {
            return;
        }

        event.preventDefault();
        const slug = trigger.dataset.quickView;
        if (slug) {
            openModal(slug);
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener("click", closeModal);
    }

    modal.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !modal.classList.contains("hidden")) {
            closeModal();
        }
    });
});
