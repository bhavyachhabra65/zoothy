document.addEventListener("DOMContentLoaded", () => {

    const quantityInputs = document.querySelectorAll(
        'input[name="quantity"], input[name="low_stock_level"]'
    );

    quantityInputs.forEach((input) => {
        input.addEventListener("input", () => {
            if (input.value && Number(input.value) < 0) {
                input.value = "0";
            }
        });
    });

});
