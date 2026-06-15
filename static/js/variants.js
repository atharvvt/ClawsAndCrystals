document.addEventListener("DOMContentLoaded", () => {
    const variantsData = document.getElementById("variants-data");

    if (!variantsData) {
        return;
    }

    const variants = JSON.parse(variantsData.textContent);
    const addToCartBtn = document.getElementById("add-to-cart-btn");
    const displayPrice = document.getElementById("display-price");
    const displaySku = document.getElementById("display-sku");
    const displayStock = document.getElementById("display-stock");
    const notifyVariantId = document.getElementById("notify-variant-id");
    const productActions = document.getElementById("product-actions");
    const baseAddUrl = addToCartBtn ? addToCartBtn.href.split("?")[0] : "";

    const getSelectedValues = () => {
        const values = {};
        document.querySelectorAll(".variant-select").forEach((select) => {
            values[select.dataset.field] = select.value;
        });
        return values;
    };

    const findVariant = () => {
        const selected = getSelectedValues();
        return variants.find((variant) => {
            return Object.keys(selected).every((field) => {
                if (!selected[field]) {
                    return true;
                }
                return variant[field] === selected[field];
            });
        });
    };

    const updateUI = () => {
        const variant = findVariant();

        if (!variant) {
            return;
        }

        if (displayPrice) {
            displayPrice.textContent = `₹${variant.price}`;
        }

        if (displaySku) {
            displaySku.textContent = variant.sku || "—";
        }

        if (displayStock) {
            if (variant.stock > 0) {
                displayStock.textContent = "In Stock";
                displayStock.className = "text-green-600";
            } else {
                displayStock.textContent = "Out of Stock";
                displayStock.className = "text-red-500";
            }
        }

        if (notifyVariantId) {
            notifyVariantId.value = variant.id;
        }

        if (addToCartBtn) {
            addToCartBtn.href = `${baseAddUrl}?variant=${variant.id}`;
        }
    };

    document.querySelectorAll(".variant-select").forEach((select) => {
        select.addEventListener("change", updateUI);
    });

    updateUI();
});
