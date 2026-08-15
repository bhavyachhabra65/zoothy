document.addEventListener(
    "DOMContentLoaded",
    () => {

        [
            "businessGstin",
            "customerGstin",
            "shippingGstin"
        ].forEach((id) => {

            const input =
                document.getElementById(id);

            if (!input) {
                return;
            }

            input.addEventListener("input", () => {
                input.value =
                    input.value
                        .toUpperCase()
                        .replace(/[^A-Z0-9]/g, "")
                        .slice(0, 15);
            });

        });

        /* ==================================================
           ELEMENTS
        ================================================== */

        const form =
            document.getElementById(
                "invoiceForm"
            );


        const itemsContainer =
            document.getElementById(
                "invoiceItems"
            );


        const addItemButton =
            document.getElementById(
                "addItemButton"
            );


        const discountInput =
            document.getElementById(
                "discount"
            );


        const subtotalElement =
            document.getElementById(
                "subtotal"
            );


        const totalElement =
            document.getElementById(
                "total"
            );


        const shippingSameAsBilling =
            document.getElementById(
                "shippingSameAsBilling"
            );


        const customerName =
            document.getElementById(
                "customerName"
            );


        const customerAddress =
            document.getElementById(
                "customerAddress"
            );


        const customerGstin =
            document.getElementById(
                "customerGstin"
            );


        const shippingName =
            document.getElementById(
                "shippingName"
            );


        const shippingAddress =
            document.getElementById(
                "shippingAddress"
            );


        const shippingGstin =
            document.getElementById(
                "shippingGstin"
            );


        let itemIndex = 1;


        /* ==================================================
           INITIALIZATION
        ================================================== */

        setDefaultInvoiceDate();

        addItemButton.addEventListener(
            "click",
            addItem
        );


        itemsContainer.addEventListener(
            "click",
            handleItemClick
        );


        itemsContainer.addEventListener(
            "input",
            handleItemInput
        );


        discountInput.addEventListener(
            "input",
            updatePreview
        );


        shippingSameAsBilling.addEventListener(
            "change",
            syncShippingAddress
        );


        customerName.addEventListener(
            "input",
            syncShippingAddress
        );


        customerAddress.addEventListener(
            "input",
            syncShippingAddress
        );


        customerGstin.addEventListener(
            "input",
            syncShippingAddress
        );


        form.addEventListener(
            "submit",
            submitInvoice
        );


        updateRemoveButtons();

        syncShippingAddress();

        updatePreview();


        /* ==================================================
           DATE
        ================================================== */

        function setDefaultInvoiceDate() {

            const input =
                document.getElementById(
                    "invoiceDate"
                );


            if (
                !input ||
                input.value
            ) {
                return;
            }


            const today =
                new Date();


            const year =
                today.getFullYear();


            const month =
                String(
                    today.getMonth() + 1
                ).padStart(
                    2,
                    "0"
                );


            const day =
                String(
                    today.getDate()
                ).padStart(
                    2,
                    "0"
                );


            input.value =
                `${year}-${month}-${day}`;
        }


        /* ==================================================
           SHIPPING
        ================================================== */

        function syncShippingAddress() {

            const same =
                shippingSameAsBilling.checked;


            if (same) {

                shippingName.value =
                    customerName.value;

                shippingAddress.value =
                    customerAddress.value;

                shippingGstin.value =
                    customerGstin.value;
            }


            shippingName.readOnly =
                same;

            shippingAddress.readOnly =
                same;

            shippingGstin.readOnly =
                same;
        }


        /* ==================================================
           ADD ITEM
        ================================================== */

        function addItem() {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "z-invoice-item";


            item.innerHTML = `
                <div class="z-item-top">

                    <div class="z-item-field z-item-name-field">

                        <label>
                            Item*
                        </label>

                        <input
                            type="text"
                            class="z-input item-name"
                            name="items[${itemIndex}][name]"
                            placeholder="Product / Service"
                            maxlength="150"
                            required
                        >

                    </div>


                    <div class="z-item-field z-item-hsn-field">

                        <label>
                            HSN / SAC*
                        </label>

                        <input
                            type="text"
                            class="z-input item-hsn"
                            name="items[${itemIndex}][hsn_code]"
                            placeholder="HSN / SAC"
                            maxlength="20"
                            autocomplete="off"
                            required
                        >

                    </div>

                </div>


                <div class="z-item-bottom">

                    <div class="z-item-field z-item-qty-field">

                        <label>
                            Qty*
                        </label>

                        <input
                            type="number"
                            class="z-input item-quantity"
                            name="items[${itemIndex}][quantity]"
                            min="0.01"
                            step="0.01"
                            value="1"
                            required
                        >

                    </div>


                    <div class="z-item-field z-item-price-field">

                        <label>
                            Price*
                        </label>

                        <input
                            type="number"
                            class="z-input item-price"
                            name="items[${itemIndex}][price]"
                            min="0"
                            step="0.01"
                            value="0"
                            onfocus="if (this.value === '0') this.value = ''"
                            required
                        >

                    </div>


                    <div class="z-item-field z-item-gst-field">

                        <label>
                            GST*
                        </label>

                        <select
                            class="z-input item-gst"
                            name="items[${itemIndex}][gst_rate]"
                            required
                        >

                            <option value="0">
                                0%
                            </option>

                            <option value="5">
                                5%
                            </option>

                            <option value="12">
                                12%
                            </option>

                            <option value="18" selected>
                                18%
                            </option>

                            <option value="28">
                                28%
                            </option>

                        </select>

                    </div>


                    <div class="z-item-amount-field">

                        <label>
                            Amount
                        </label>

                        <span
                            class="z-invoice-item-amount"
                        >
                            ₹0.00
                        </span>

                    </div>


                    <button
                        type="button"
                        class="z-item-remove"
                        aria-label="Remove item"
                    >
                        ×
                    </button>

                </div>
            `;


            itemsContainer.appendChild(
                item
            );


            itemIndex++;


            updateRemoveButtons();

            updatePreview();
        }


        /* ==================================================
           REMOVE ITEM
        ================================================== */

        function handleItemClick(
            event
        ) {

            const button =
                event.target.closest(
                    ".z-item-remove"
                );


            if (!button) {
                return;
            }


            const item =
                button.closest(
                    ".z-invoice-item"
                );


            if (!item) {
                return;
            }


            item.remove();


            updateRemoveButtons();

            updatePreview();
        }


        function updateRemoveButtons() {

            const items =
                itemsContainer.querySelectorAll(
                    ".z-invoice-item"
                );


            items.forEach(
                (item) => {

                    const button =
                        item.querySelector(
                            ".z-item-remove"
                        );


                    button.disabled =
                        items.length === 1;
                }
            );
        }


        /* ==================================================
           ITEM INPUT
        ================================================== */

        function handleItemInput(
            event
        ) {

            if (
                event.target.matches(
                    ".item-quantity, .item-price, .item-gst"
                )
            ) {

                updatePreview();
            }
        }


        /* ==================================================
           LIVE PREVIEW
        ================================================== */

        function updatePreview() {

            const items =
                InvoiceService.buildItems(
                    itemsContainer
                );


            const discount =
                Number(
                    discountInput.value
                ) || 0;


            const totals =
                InvoiceService.calculatePreview(
                    items,
                    discount
                );


            items.forEach(
                (item, index) => {

                    const row =
                        itemsContainer.querySelectorAll(
                            ".z-invoice-item"
                        )[index];


                    const amountElement =
                        row.querySelector(
                            ".z-invoice-item-amount"
                        );


                    const calculation =
                        InvoiceService.calculateItem(
                            item
                        );


                    amountElement.textContent =
                        InvoiceService.formatAmount(
                            calculation.amount
                        );
                }
            );


            subtotalElement.textContent =
                InvoiceService.formatAmount(
                    totals.subtotal
                );


            totalElement.textContent =
                InvoiceService.formatAmount(
                    totals.total
                );
        }


        /* ==================================================
           SUBMIT
        ================================================== */

        async function submitInvoice(
            event
        ) {

            event.preventDefault();


            try {

                const items =
                    InvoiceService.buildItems(
                        itemsContainer
                    );


                const response =
                    await InvoiceService.submit(
                        form,
                        items
                    );


                const result =
                    await InvoiceService.getResponseData(
                        response
                    );


                if (
                    !response.ok
                ) {

                    if (
                        result.type === "json"
                    ) {

                        alert(
                            result.data.message ||
                            "Unable to create invoice."
                        );

                    } else {

                        alert(
                            "Unable to create invoice."
                        );
                    }


                    return;
                }


                if (
                    result.type !== "html"
                ) {

                    alert(
                        "Unexpected response from server."
                    );

                    return;
                }


                printInvoice(
                    result.data
                );

            } catch (error) {

                console.error(
                    "Invoice submission failed:",
                    error
                );


                alert(
                    "Unable to create invoice."
                );
            }
        }


        /* ==================================================
           PRINT
        ================================================== */

        function printInvoice(
            html
        ) {

            const printWindow =
                window.open(
                    "",
                    "invoicePrintWindow",
                    "width=1000,height=800,resizable=yes,scrollbars=yes"
                );


            if (!printWindow) {

                alert(
                    "Please allow pop-ups to print the invoice."
                );

                return;
            }


            printWindow.document.open();

            printWindow.document.write(
                html
            );

            printWindow.document.close();
        }

    }

    
);