document.addEventListener("DOMContentLoaded", () => {
    const copyBtn = document.getElementById("copy-link-btn");

    if (!copyBtn) {
        return;
    }

    copyBtn.addEventListener("click", async () => {
        const url = copyBtn.dataset.shareUrl || window.location.href;

        try {
            await navigator.clipboard.writeText(url);
            copyBtn.textContent = "Link copied!";
            setTimeout(() => {
                copyBtn.textContent = "Copy link";
            }, 2000);
        } catch (error) {
            copyBtn.textContent = "Copy failed";
        }
    });
});
