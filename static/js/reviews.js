document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("review-modal");

    if (!modal) {
        return;
    }

    const openModal = () => {
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("review-modal-open");
    };

    const closeModal = () => {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("review-modal-open");
    };

    document.querySelectorAll("[data-review-open]").forEach((trigger) => {
        trigger.addEventListener("click", (event) => {
            event.preventDefault();
            openModal();
        });
    });

    modal.querySelectorAll("[data-review-close]").forEach((trigger) => {
        trigger.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && modal.classList.contains("is-open")) {
            closeModal();
        }
    });

    modal.querySelectorAll("[data-star-input]").forEach((group) => {
        const inputs = [...group.querySelectorAll(".review-stars__input")];

        const updateStars = () => {
            const checked = inputs.find((input) => input.checked);
            const value = checked ? Number(checked.value) : 0;

            inputs.forEach((input) => {
                const star = input.nextElementSibling;
                star.classList.toggle("is-active", Number(input.value) <= value);
            });
        };

        inputs.forEach((input) => {
            input.addEventListener("change", updateStars);
        });

        updateStars();
    });

    if (modal.classList.contains("is-open")) {
        document.body.classList.add("review-modal-open");
    }
});
