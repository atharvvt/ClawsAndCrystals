document.addEventListener("DOMContentLoaded", () => {
    const mainImage = document.getElementById("main-product-image");
    const thumbnails = document.querySelectorAll("[data-gallery-thumb]");

    if (!mainImage || !thumbnails.length) {
        return;
    }

    thumbnails.forEach((thumb) => {
        thumb.addEventListener("click", () => {
            mainImage.src = thumb.dataset.fullUrl;
            mainImage.alt = thumb.dataset.alt || mainImage.alt;

            thumbnails.forEach((item) => {
                item.classList.toggle("is-active", item === thumb);
            });
        });
    });
});
