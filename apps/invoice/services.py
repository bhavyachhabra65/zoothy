import re
from datetime import date

from .schemas import Invoice, InvoiceItem
from .validators import ValidationError


GST_STATE_CODES = {
    "01": "Jammu and Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "26": "Dadra and Nagar Haveli and Daman and Diu",
    "27": "Maharashtra",
    "28": "Andhra Pradesh",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman and Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
}


class InvoiceService:

    ALLOWED_GST_RATES = {
        0,
        5,
        12,
        18,
        28
    }

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def clean(value):
        return str(value or "").strip()


    @staticmethod
    def extract_state_code(gstin):

        gstin = (
            str(gstin or "")
            .strip()
            .upper()
        )

        if not gstin:
            return None

        if not re.fullmatch(
            r"\d{2}[A-Z0-9]{13}",
            gstin
        ):
            raise InvoiceValidationError(
                "Enter a valid GSTIN."
            )

        state_code = gstin[:2]

        if state_code not in GST_STATE_CODES:
            raise InvoiceValidationError(
                "GSTIN contains an invalid state code."
            )

        return state_code

    @classmethod
    def _calculate_gst_split(
        cls,
        business_gstin,
        customer_gstin,
        total_tax):

        business_state_code = \
            cls.extract_state_code(
                business_gstin
            )

        customer_state_code = \
            cls.extract_state_code(
                customer_gstin
            )

        # GSTIN not provided
        if not business_state_code or not customer_state_code:

            return (
                0,
                0,
                0
            )

        if (
            business_state_code !=
            customer_state_code
        ):

            return (
                0,
                0,
                total_tax
            )

        cgst = round(
            total_tax / 2,
            2
        )

        sgst = round(
            total_tax - cgst,
            2
        )

        return (
            cgst,
            sgst,
            0
        )


    @staticmethod
    def parse_date(
        value,
        field_name,
        required=True
    ):

        value = InvoiceService.clean(
            value
        )

        if not value:

            if required:
                raise ValueError(
                    f"{field_name} is required."
                )

            return None

        try:

            return date.fromisoformat(
                value
            )

        except ValueError:

            raise ValueError(
                f"{field_name} is invalid."
            )


    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def validate_invoice_data(data):

        # ------------------------------------------------------
        # Invoice Number
        # ------------------------------------------------------

        invoice_number = InvoiceService.clean(
            data.get("invoice_number")
        )

        if not invoice_number:

            raise ValueError(
                "Invoice number is required."
            )

        if len(invoice_number) > 50:

            raise ValueError(
                "Invoice number cannot exceed 50 characters."
            )


        # ------------------------------------------------------
        # Dates
        # ------------------------------------------------------

        invoice_date = InvoiceService.parse_date(
            data.get("invoice_date"),
            "Invoice date"
        )

        due_date = InvoiceService.parse_date(
            data.get("due_date"),
            "Due date",
            required=False
        )

        today = date.today()

        if invoice_date > today:

            raise ValueError(
                "Invoice date cannot be in the future."
            )

        if due_date and due_date < invoice_date:

            raise ValueError(
                "Due date cannot be before invoice date."
            )


        # ------------------------------------------------------
        # Business
        # ------------------------------------------------------

        business_name = InvoiceService.clean(
            data.get("business_name")
        )

        business_address = InvoiceService.clean(
            data.get("business_address")
        )

        business_gstin = InvoiceService.clean(
            data.get("business_gstin")
        ).upper()

        if not business_name:

            raise ValueError(
                "Business name is required."
            )

        if len(business_name) > 150:

            raise ValueError(
                "Business name cannot exceed 150 characters."
            )

        if not business_address:

            raise ValueError(
                "Business address is required."
            )

        if len(business_address) > 500:

            raise ValueError(
                "Business address cannot exceed 500 characters."
            )
        
        business_state_code = None
        if business_gstin: 
            business_state_code = (
                InvoiceService.extract_state_code(
                    business_gstin
                )
            )


        # ------------------------------------------------------
        # Customer / Bill To
        # ------------------------------------------------------

        customer_name = InvoiceService.clean(
            data.get("customer_name")
        )

        customer_address = InvoiceService.clean(
            data.get("customer_address")
        )

        customer_gstin = InvoiceService.clean(
            data.get("customer_gstin")
        ).upper()

        if not customer_name:

            raise ValueError(
                "Customer name is required."
            )

        if len(customer_name) > 150:

            raise ValueError(
                "Customer name cannot exceed 150 characters."
            )

        if not customer_address:

            raise ValueError(
                "Bill To address is required."
            )

        if len(customer_address) > 500:

            raise ValueError(
                "Bill To address cannot exceed 500 characters."
            )

        customer_state_code = None
        if customer_gstin:
                customer_state_code = (
                InvoiceService.extract_state_code(
                    customer_gstin
                )
            )


        # ------------------------------------------------------
        # Shipping / Ship To
        # ------------------------------------------------------

        shipping_name = InvoiceService.clean(
            data.get("shipping_name")
        )

        shipping_address = InvoiceService.clean(
            data.get("shipping_address")
        )

        shipping_gstin = InvoiceService.clean(
            data.get("shipping_gstin")
        ).upper()

        # Shipping is optional.
        # But if any shipping information is entered,
        # require the required shipping fields.

        if shipping_name:

            if len(shipping_name) > 150:

                raise ValueError(
                    "Shipping name cannot exceed 150 characters."
                )

        if shipping_address:

            if len(shipping_address) > 500:

                raise ValueError(
                    "Shipping address cannot exceed 500 characters."
                )

        if shipping_gstin:

            InvoiceService.extract_state_code(
                shipping_gstin
            )


        # ------------------------------------------------------
        # Items
        # ------------------------------------------------------

        raw_items = data.get(
            "items",
            []
        )

        if not raw_items:

            raise ValueError(
                "Please add at least one item."
            )


        items = []

        subtotal = 0.0


        for index, item in enumerate(
            raw_items,
            start=1
        ):

            if not isinstance(
                item,
                dict
            ):

                raise ValueError(
                    f"Item {index} is invalid."
                )


            # --------------------------------------------------
            # Item Name
            # --------------------------------------------------

            name = InvoiceService.clean(
                item.get("name")
            )

            if not name:

                raise ValueError(
                    f"Item {index}: item name is required."
                )

            if len(name) > 150:

                raise ValueError(
                    f"Item {index}: item name cannot exceed 150 characters."
                )


            # --------------------------------------------------
            # HSN / SAC
            # --------------------------------------------------

            hsn_code = InvoiceService.clean(
                item.get("hsn_code")
            )

            if not hsn_code:

                raise ValueError(
                    f"Item {index}: HSN / SAC is required."
                )

            if len(hsn_code) > 20:

                raise ValueError(
                    f"Item {index}: HSN / SAC cannot exceed 20 characters."
                )


            # --------------------------------------------------
            # Quantity
            # --------------------------------------------------

            try:

                quantity = float(
                    item.get("quantity")
                )

            except (
                TypeError,
                ValueError
            ):

                raise ValueError(
                    f"Item {index}: quantity is invalid."
                )

            if quantity <= 0:

                raise ValueError(
                    f"Item {index}: quantity must be greater than 0."
                )


            # --------------------------------------------------
            # Price
            # --------------------------------------------------

            try:

                price = float(
                    item.get("price")
                )

            except (
                TypeError,
                ValueError
            ):

                raise ValueError(
                    f"Item {index}: price is invalid."
                )

            if price < 0:

                raise ValueError(
                    f"Item {index}: price cannot be negative."
                )


            # --------------------------------------------------
            # GST
            # --------------------------------------------------

            try:

                gst_rate = float(
                    item.get("gst_rate")
                )

            except (
                TypeError,
                ValueError
            ):

                raise ValueError(
                    f"Item {index}: GST rate is invalid."
                )

            if gst_rate not in InvoiceService.ALLOWED_GST_RATES:

                raise ValueError(
                    f"Item {index}: GST must be 0%, 5%, 12%, 18% or 28%."
                )


            # --------------------------------------------------
            # Calculate Item
            # --------------------------------------------------

            taxable_amount = (
                quantity * price
            )

            subtotal += taxable_amount


            items.append(
                InvoiceItem(

                    name=name,

                    hsn_code=hsn_code,

                    quantity=quantity,

                    price=price,

                    gst_rate=gst_rate,

                    taxable_amount=taxable_amount,

                    discount_amount=0,

                    tax_amount=0,

                    amount=taxable_amount
                )
            )


        subtotal = round(
            subtotal,
            2
        )


        # ------------------------------------------------------
        # Discount
        # ------------------------------------------------------

        discount_value = InvoiceService.clean(
            data.get("discount")
        )

        try:

            discount = float(
                discount_value or 0
            )

        except ValueError:

            raise ValueError(
                "Discount is invalid."
            )

        if discount < 0:

            raise ValueError(
                "Discount cannot be negative."
            )

        if discount > subtotal:

            raise ValueError(
                "Discount cannot be greater than subtotal."
            )


        # ------------------------------------------------------
        # Return validated data
        # ------------------------------------------------------

        return {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date.isoformat(),
            "due_date": (
                due_date.isoformat()
                if due_date
                else ""
            ),

            "business_name": business_name,
            "business_address": business_address,
            "business_gstin": business_gstin,

            "customer_name": customer_name,
            "customer_address": customer_address,
            "customer_gstin": customer_gstin,

            "shipping_name": shipping_name,
            "shipping_address": shipping_address,
            "shipping_gstin": shipping_gstin,

            "business_state_code": business_state_code,
            "customer_state_code": customer_state_code,

            "items": items,

            "subtotal": subtotal,
            "discount": round(
                discount,
                2
            )
        }


    # ==========================================================
    # BUILD INVOICE
    # ==========================================================

    @staticmethod
    def build_invoice(data):

        # ------------------------------------------------------
        # Validate everything first
        # ------------------------------------------------------

        InvoiceService.validate_invoice_data(
            data
        )


        # ------------------------------------------------------
        # GSTIN
        # ------------------------------------------------------

        business_gstin = InvoiceService.clean(
            data.get("business_gstin")
        ).upper()

        customer_gstin = InvoiceService.clean(
            data.get("customer_gstin")
        ).upper()


        # ------------------------------------------------------
        # Shipping
        # ------------------------------------------------------

        shipping_name = InvoiceService.clean(
            data.get("shipping_name")
        )

        shipping_address = InvoiceService.clean(
            data.get("shipping_address")
        )

        shipping_gstin = InvoiceService.clean(
            data.get("shipping_gstin")
        ).upper()


        # ------------------------------------------------------
        # State Codes
        # ------------------------------------------------------

        business_state_code = (
            InvoiceService.extract_state_code(
                business_gstin
            )
        )

        customer_state_code = (
            InvoiceService.extract_state_code(
                customer_gstin
            )
        )

        place_of_supply = ""

        if customer_state_code:
            place_of_supply = GST_STATE_CODES.get(
                customer_state_code,
                customer_state_code
            )

        # ------------------------------------------------------
        # Interstate
        # ------------------------------------------------------

        is_inter_state = (
            business_state_code
            != customer_state_code
        )


        # ------------------------------------------------------
        # Items
        # ------------------------------------------------------

        items = []

        subtotal = 0.0


        for item in data.get(
            "items",
            []
        ):

            quantity = float(
                item.get(
                    "quantity",
                    0
                )
            )

            price = float(
                item.get(
                    "price",
                    0
                )
            )

            gst_rate = float(
                item.get(
                    "gst_rate",
                    0
                )
            )


            taxable_amount = (
                quantity * price
            )

            subtotal += taxable_amount


            items.append(
                InvoiceItem(

                    name=InvoiceService.clean(
                        item.get("name")
                    ),

                    hsn_code=InvoiceService.clean(
                        item.get("hsn_code")
                    ),

                    quantity=quantity,

                    price=price,

                    gst_rate=gst_rate,

                    taxable_amount=taxable_amount,

                    discount_amount=0,

                    tax_amount=0,

                    amount=taxable_amount
                )
            )


        subtotal = round(
            subtotal,
            2
        )


        # ------------------------------------------------------
        # Discount
        # ------------------------------------------------------

        discount = float(
            data.get(
                "discount",
                0
            ) or 0
        )


        # Validation has already guaranteed that
        # discount is between 0 and subtotal.

        taxable_total = (
            subtotal - discount
        )


        # ------------------------------------------------------
        # Tax Calculation
        # ------------------------------------------------------

        total_tax = 0.0


        for index, item in enumerate(
            items
        ):

            if subtotal > 0:

                if index == len(items) - 1:

                    discount_amount = round(
                        discount
                        - sum(
                            previous.discount_amount
                            for previous in items[:-1]
                        ),
                        2
                    )

                else:

                    discount_amount = round(
                        discount
                        * item.taxable_amount
                        / subtotal,
                        2
                    )

            else:

                discount_amount = 0


            item.discount_amount = (
                discount_amount
            )


            item.taxable_amount = round(
                item.taxable_amount
                - discount_amount,
                2
            )


            item.tax_amount = round(
                item.taxable_amount
                * item.gst_rate
                / 100,
                2
            )


            item.amount = round(
                item.taxable_amount
                + item.tax_amount,
                2
            )


            total_tax += item.tax_amount


        total_tax = round(
            total_tax,
            2
        )

        cgst, sgst, igst = (
        InvoiceService._calculate_gst_split(
            data["business_gstin"],
            data["customer_gstin"],
            total_tax
        )
    )


        # ------------------------------------------------------
        # Total
        # ------------------------------------------------------

        total = round(
            taxable_total
            + total_tax,
            2
        )

        # ------------------------------------------------------
        # Invoice
        # ------------------------------------------------------

        return Invoice(

            invoice_number=InvoiceService.clean(
                data.get("invoice_number")
            ),

            invoice_date=data.get(
                "invoice_date",
                ""
            ),

            due_date=data.get(
                "due_date",
                ""
            ),

            business_name=InvoiceService.clean(
                data.get("business_name")
            ),

            business_address=InvoiceService.clean(
                data.get("business_address")
            ),

            business_gstin=business_gstin,

            customer_name=InvoiceService.clean(
                data.get("customer_name")
            ),

            customer_address=InvoiceService.clean(
                data.get("customer_address")
            ),

            customer_gstin=customer_gstin,

            shipping_name=shipping_name,

            shipping_address=shipping_address,

            shipping_gstin=shipping_gstin,

            business_state_code=business_state_code,

            customer_state_code=customer_state_code,

            place_of_supply = place_of_supply,

            items=items,

            subtotal=round(
                subtotal,
                2
            ),

            discount=round(
                discount,
                2
            ),

            cgst=cgst,
            sgst=sgst,
            igst=igst,

            total_tax=total_tax,

            total=total
        )