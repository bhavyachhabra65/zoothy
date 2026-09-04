(function () {
    "use strict";

    const body = document.getElementById("saleItemsBody");
    const addButton = document.getElementById("addSaleItem");
    const template = document.getElementById("saleItemTemplate");

    if (!body || !addButton || !template) {
        return;
    }

    function money(value) {
        return `₹${Number(value || 0).toFixed(2)}`;
    }

    function updateRow(row) {
        const product = row.querySelector(".z-sale-product");
        const quantity = row.querySelector(".z-sale-quantity");
        const price = row.querySelector(".z-sale-price");
        const gst = row.querySelector(".z-sale-gst");
        const unit = row.querySelector(".z-sale-unit");
        const lineTotal = row.querySelector(".z-sale-line-total");

        if (!product || !quantity || !price || !gst || !unit || !lineTotal) {
            return { subtotal: 0, tax: 0, total: 0 };
        }

        const option = product.options[product.selectedIndex];
        const defaultPrice = option ? Number(option.dataset.price || 0) : 0;
        const gstRate = option ? Number(option.dataset.gst || 0) : 0;
        const productUnit = option ? option.dataset.unit || "" : "";

        if (product.value && (!price.value || Number(price.value) === 0)) {
            price.value = defaultPrice.toFixed(2);
        }

        const quantityValue = Number(quantity.value || 0);
        const priceValue = Number(price.value || 0);
        const lineSubtotal = quantityValue * priceValue;
        const tax = lineSubtotal * gstRate / 100;
        const total = lineSubtotal + tax;

        gst.textContent = `${gstRate.toFixed(2).replace(/\.00$/, "")}%`;
        unit.textContent = productUnit || "—";
        lineTotal.textContent = money(total);

        return {
            subtotal: lineSubtotal,
            tax,
            total
        };
    }

    function updateTotals() {
        let subtotal = 0;
        let tax = 0;

        body.querySelectorAll(".z-sale-item-row").forEach((row) => {
            const values = updateRow(row);
            subtotal += values.subtotal;
            tax += values.tax;
        });

        const subtotalElement = document.getElementById("saleSubtotal");
        const taxElement = document.getElementById("saleTax");
        const totalElement = document.getElementById("saleTotal");

        if (subtotalElement) {
            subtotalElement.textContent = money(subtotal);
        }

        if (taxElement) {
            taxElement.textContent = money(tax);
        }

        if (totalElement) {
            totalElement.textContent = money(subtotal + tax);
        }
    }

    function resetRow(row) {
        const product = row.querySelector(".z-sale-product");
        const quantity = row.querySelector(".z-sale-quantity");
        const price = row.querySelector(".z-sale-price");

        if (product) {
            product.value = "";
        }

        if (quantity) {
            quantity.value = "1";
        }

        if (price) {
            price.value = "0";
        }
    }

    function bindRow(row) {
        row.querySelectorAll("input, select").forEach((field) => {
            field.addEventListener("input", updateTotals);
            field.addEventListener("change", updateTotals);
        });

        const removeButton = row.querySelector(".z-sale-remove-row");

        if (removeButton) {
            removeButton.addEventListener("click", function () {
                const rows = body.querySelectorAll(".z-sale-item-row");

                if (rows.length === 1) {
                    resetRow(row);
                } else {
                    row.remove();
                }

                updateTotals();
            });
        }
    }

    body.querySelectorAll(".z-sale-item-row").forEach(bindRow);

    addButton.addEventListener("click", function () {
        const row = template.content.firstElementChild.cloneNode(true);

        body.appendChild(row);
        bindRow(row);
        updateTotals();

        const product = row.querySelector(".z-sale-product");

        if (product) {
            product.focus();
        }
    });

    updateTotals();
}());
