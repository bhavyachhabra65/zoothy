document.addEventListener("DOMContentLoaded", () => {

    const hsnInputs = document.querySelectorAll(
        ".z-product-hsn-input"
    );

    hsnInputs.forEach((input) => {
        input.addEventListener("input", () => {
            input.value = input.value
                .toUpperCase()
                .replace(/[^0-9A-Z]/g, "")
                .slice(0, 20);
        });
    });

    const deleteForms = document.querySelectorAll(
        "[data-delete-product]"
    );

    deleteForms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.confirm("Delete this product?")) {
                event.preventDefault();
            }
        });
    });

});
