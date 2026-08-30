document.addEventListener("DOMContentLoaded", () => {

    const gstinInputs = document.querySelectorAll(
        ".z-gstin-input"
    );

    gstinInputs.forEach((input) => {
        input.addEventListener("input", () => {
            input.value = input.value
                .toUpperCase()
                .replace(/[^0-9A-Z]/g, "")
                .slice(0, 15);
        });
    });

    const phoneInputs = document.querySelectorAll(
        'input[name="phone"]'
    );

    phoneInputs.forEach((input) => {
        input.addEventListener("input", () => {
            input.value = input.value
                .replace(/\D/g, "")
                .slice(0, 10);
        });
    });

    const deleteForms = document.querySelectorAll(
        "[data-delete-customer]"
    );

    deleteForms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.confirm("Delete this customer?")) {
                event.preventDefault();
            }
        });
    });

});
