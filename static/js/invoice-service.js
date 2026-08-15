/* ==========================================================
   INVOICE SERVICE
   ==========================================================

   Responsible for invoice calculations and data handling.

   This file contains invoice-related logic.

   It does NOT manipulate the page UI directly.
========================================================== */


/* ==========================================================
   CONSTANTS
========================================================== */

const InvoiceService = {

    GST_RATES: [
        0,
        5,
        12,
        18,
        28
    ],


    /* ======================================================
       ITEM CALCULATION
    ====================================================== */

    calculateItem(item) {

        const quantity =
            Number(item.quantity) || 0;

        const price =
            Number(item.price) || 0;

        const gstRate =
            Number(item.gst_rate) || 0;


        const taxableAmount =
            quantity * price;


        const taxAmount =
            taxableAmount *
            gstRate /
            100;


        const amount =
            taxableAmount +
            taxAmount;


        return {

            taxableAmount,

            taxAmount,

            amount
        };
    },


    /* ======================================================
       CALCULATE SUBTOTAL
    ====================================================== */

    calculateSubtotal(items) {

        return items.reduce(
            (subtotal, item) => {

                const calculation =
                    this.calculateItem(item);


                return (
                    subtotal +
                    calculation.taxableAmount
                );

            },
            0
        );
    },


    /* ======================================================
       CALCULATE TOTAL TAX
    ====================================================== */

    calculateTax(items) {

        return items.reduce(
            (tax, item) => {

                const calculation =
                    this.calculateItem(item);


                return (
                    tax +
                    calculation.taxAmount
                );

            },
            0
        );
    },


    /* ======================================================
       CALCULATE TOTAL
    ====================================================== */

    calculateTotal(
        subtotal,
        discount,
        tax
    ) {

        const taxableTotal =
            Math.max(
                subtotal - discount,
                0
            );


        return (
            taxableTotal +
            tax
        );
    },


    /* ======================================================
       CALCULATE PREVIEW
    ====================================================== */

    calculatePreview(
        items,
        discount
    ) {

        const subtotal =
            this.calculateSubtotal(
                items
            );


        const tax =
            this.calculateTax(
                items
            );


        const total =
            this.calculateTotal(
                subtotal,
                discount,
                tax
            );


        return {

            subtotal:
                this.round(subtotal),

            discount:
                this.round(discount),

            tax:
                this.round(tax),

            total:
                this.round(total)
        };
    },


    /* ======================================================
       BUILD ITEM DATA
    ====================================================== */

    buildItems(container) {

        const items = [];


        container
            .querySelectorAll(
                ".z-invoice-item"
            )
            .forEach((item) => {

                items.push({

                    name:
                        item.querySelector(
                            ".item-name"
                        )?.value.trim() || "",


                    hsn_code:
                        item.querySelector(
                            ".item-hsn"
                        )?.value.trim() || "",


                    quantity:
                        item.querySelector(
                            ".item-quantity"
                        )?.value || "",


                    price:
                        item.querySelector(
                            ".item-price"
                        )?.value || "",


                    gst_rate:
                        item.querySelector(
                            ".item-gst"
                        )?.value || ""

                });

            });


        return items;
    },


    /* ======================================================
       BUILD FORM DATA
    ====================================================== */

    buildFormData(
        form,
        items
    ) {

        const formData =
            new FormData(form);


        formData.delete(
            "items"
        );


        formData.append(
            "items",
            JSON.stringify(items)
        );


        return formData;
    },


    /* ======================================================
       SUBMIT INVOICE
    ====================================================== */

    async submit(
        form,
        items
    ) {

        const formData =
            this.buildFormData(
                form,
                items
            );


        const response =
            await fetch(
                form.action,
                {
                    method:
                        form.method || "POST",

                    body:
                        formData
                }
            );


        return response;
    },


    /* ======================================================
       RESPONSE
    ====================================================== */

    async getResponseData(
        response
    ) {

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        if (
            contentType.includes(
                "application/json"
            )
        ) {

            return {
                type: "json",

                data:
                    await response.json()
            };
        }


        return {
            type: "html",

            data:
                await response.text()
        };
    },


    /* ======================================================
       FORMAT MONEY
    ====================================================== */

    formatAmount(amount) {

        return `₹${this.round(amount).toFixed(2)}`;
    },


    /* ======================================================
       ROUND
    ====================================================== */

    round(value) {

        return Math.round(
            (Number(value) + Number.EPSILON) *
            100
        ) / 100;
    }

};