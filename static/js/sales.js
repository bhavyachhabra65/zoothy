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

        const option = product.options[product.selectedIndex];
        const defaultPrice = option ? Number(option.dataset.price || 0) : 0;
        const gstRate = option ? Number(option.dataset.gst || 0) : 0;
        const productUnit = option ? option.dataset.unit || "" : "";

        if (product.value && (!price.value || Number(price.value) === 0)) {
            price.value = defaultPrice.toFixed(2);
        }

        const lineSubtotal = Number(quantity.value || 0) * Number(price.value || 0);
        const tax = lineSubtotal * gstRate / 100;
        const total = lineSubtotal + tax;

        gst.textContent = `${gstRate.toFixed(2).replace(/\.00$/, "")}%`;
        unit.textContent = productUnit || "—";
        lineTotal.textContent = money(total);

        return { subtotal: lineSubtotal, tax, total };
    }

    function updateTotals() {
        let subtotal = 0;
        let tax = 0;

        body.querySelectorAll(".z-sale-item-row").forEach((row) => {
            const values = updateRow(row);
            subtotal += values.subtotal;
            tax += values.tax;
        });

        document.getElementById("saleSubtotal").textContent = money(subtotal);
        document.getElementById("saleTax").textContent = money(tax);
        document.getElementById("saleTotal").textContent = money(subtotal + tax);
    }

    function bindRow(row) {
        row.querySelectorAll("input, select").forEach((field) => {
            field.addEventListener("input", updateTotals);
            field.addEventListener("change", updateTotals);
        });

        row.querySelector(".z-sale-remove-row").addEventListener("click", function () {
            const rows = body.querySelectorAll(".z-sale-item-row");
            if (rows.length === 1) {
                row.querySelector(".z-sale-product").value = "";
                row.querySelector(".z-sale-quantity").value = "1";
                row.querySelector(".z-sale-price").value = "0";
            } else {
                row.remove();
            }
            updateTotals();
        });
    }

    body.querySelectorAll(".z-sale-item-row").forEach(bindRow);

    addButton.addEventListener("click", function () {
        const row = template.content.firstElementChild.cloneNode(true);
        body.appendChild(row);
        bindRow(row);
        updateTotals();
        row.querySelector(".z-sale-product").focus();
    });

    updateTotals();
}());
