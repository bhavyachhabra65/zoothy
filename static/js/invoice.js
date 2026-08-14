document.addEventListener("DOMContentLoaded", () => {

    const invoiceItems = document.getElementById("invoiceItems");
    const addItemButton = document.getElementById("addItemButton");
    const discountInput = document.getElementById("discount");
    const subtotalElement = document.getElementById("subtotal");
    const totalElement = document.getElementById("total");
    const invoiceForm = document.getElementById("invoiceForm");

    let itemIndex = 1;


    function formatAmount(amount) {
        return `₹${amount.toFixed(2)}`;
    }


    function calculateItemAmount(item) {

        const quantity = parseFloat(
            item.querySelector(".item-quantity").value
        ) || 0;

        const price = parseFloat(
            item.querySelector(".item-price").value
        ) || 0;

        const gstRate = parseFloat(
            item.querySelector(".item-gst").value
        ) || 0;

        const taxableAmount = quantity * price;

        const taxAmount =
            taxableAmount * gstRate / 100;

        const amount =
            taxableAmount + taxAmount;

        item.querySelector(".z-invoice-item-amount").textContent =
            formatAmount(amount);

        return taxableAmount;
    }


    function calculateTotals() {

        let subtotal = 0;

        invoiceItems
            .querySelectorAll(".z-invoice-item")
            .forEach((item) => {
                subtotal += calculateItemAmount(item);
            });

        const discount =
            parseFloat(discountInput.value) || 0;

        const total = Math.max(subtotal - discount, 0);

        subtotalElement.textContent = formatAmount(subtotal);
        totalElement.textContent = formatAmount(total);
    }


    function createItem() {

        const item = document.createElement("div");

        item.className = "z-invoice-item";

        item.innerHTML = `
            <input
                type="text"
                class="z-input item-name"
                name="items[${itemIndex}][name]"
                placeholder="Product / Service"
                maxlength="150"
                required>

            <input
                type="text"
                class="z-input item-hsn"
                name="items[${itemIndex}][hsn_code]"
                placeholder="HSN / SAC"
                maxlength="20"
                autocomplete="off"
                required>

            <input
                type="number"
                class="z-input item-quantity"
                name="items[${itemIndex}][quantity]"
                min="0.01"
                step="0.01"
                value="1"
                required>

            <input
                type="number"
                class="z-input item-price"
                name="items[${itemIndex}][price]"
                min="0"
                step="0.01"
                value="0"
                required>

            <select
                class="z-input item-gst"
                name="items[${itemIndex}][gst_rate]"
                required>

                <option value="0">0%</option>
                <option value="5">5%</option>
                <option value="12">12%</option>
                <option value="18" selected>18%</option>
                <option value="28">28%</option>

            </select>

            <span class="z-invoice-item-amount">
                ₹0.00
            </span>

            <button
                type="button"
                class="z-item-remove"
                aria-label="Remove item">
                ×
            </button>
        `;

        invoiceItems.appendChild(item);

        itemIndex++;

        updateRemoveButtons();
        calculateTotals();
    }


    function updateRemoveButtons() {

        const items =
            invoiceItems.querySelectorAll(".z-invoice-item");

        items.forEach((item, index) => {

            const removeButton =
                item.querySelector(".z-item-remove");

            removeButton.disabled = items.length === 1;
        });
    }


    addItemButton.addEventListener("click", () => {
        createItem();
    });


    invoiceItems.addEventListener("input", (event) => {

        if (
            event.target.classList.contains("item-quantity") ||
            event.target.classList.contains("item-price") ||
            event.target.classList.contains("item-gst")
        ) {
            calculateTotals();
        }       
    });


    invoiceItems.addEventListener("click", (event) => {

        if (!event.target.classList.contains("z-item-remove")) {
            return;
        }

        event.target.closest(".z-invoice-item").remove();

        updateRemoveButtons();
        calculateTotals();
    });


    discountInput.addEventListener("input", () => {
        calculateTotals();
    });


    invoiceForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        calculateTotals();

        const items = [];

        invoiceItems
            .querySelectorAll(".z-invoice-item")
            .forEach((item) => {

                items.push({
                    name: item.querySelector(".item-name").value.trim(),
                    hsn_code: item.querySelector(".item-hsn").value.trim(),
                    quantity: item.querySelector(".item-quantity").value,
                    price: item.querySelector(".item-price").value,
                    gst_rate: item.querySelector(".item-gst").value
                });
            });

        const formData = new FormData(invoiceForm);

        formData.delete("items");

        formData.append(
            "items",
            JSON.stringify(items)
        );

        const response = await fetch(
            invoiceForm.action,
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            return;
        }

        const html = await response.text();

        document.open();
        document.write(html);
        document.close();
    });


    calculateTotals();
    updateRemoveButtons();

});