import re

from .schemas import Invoice, InvoiceItem


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

    @staticmethod
    def extract_state_code(gstin):
        gstin = gstin.strip().upper()

        if not re.fullmatch(r"\d{2}[A-Z0-9]{13}", gstin):
            raise ValueError("Invalid GSTIN")

        return gstin[:2]


    @staticmethod
    def build_invoice(data):

        business_gstin = data.get(
            "business_gstin", ""
        ).strip().upper()

        customer_gstin = data.get(
            "customer_gstin", ""
        ).strip().upper()

        supplier_state_code = (
            InvoiceService.extract_state_code(
                business_gstin
            )
        )

        customer_state_code = (
            InvoiceService.extract_state_code(
                customer_gstin
            )
        )

        is_inter_state = (
            supplier_state_code != customer_state_code
        )

        items = []
        subtotal = 0.0

        for item in data.get("items", []):

            quantity = float(
                item.get("quantity", 0)
            )

            price = float(
                item.get("price", 0)
            )

            gst_rate = float(
                item.get("gst_rate", 0)
            )

            taxable_amount = quantity * price

            subtotal += taxable_amount

            items.append(
                InvoiceItem(
                    name=item.get("name", "").strip(),
                    hsn_code=item.get("hsn_code", "").strip(),
                    quantity=quantity,
                    price=price,
                    gst_rate=gst_rate,
                    taxable_amount=taxable_amount,
                    discount_amount=0,
                    tax_amount=0,
                    amount=taxable_amount
                )
            )

        discount = float(
            data.get("discount", 0)
        )

        discount = min(
            max(discount, 0),
            subtotal
        )

        taxable_total = subtotal - discount

        total_tax = 0.0

        for index, item in enumerate(items):

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

            item.discount_amount = discount_amount

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

        total_tax = round(total_tax, 2)

        if is_inter_state:

            cgst = 0
            sgst = 0
            igst = total_tax

        else:

            cgst = round(
                total_tax / 2,
                2
            )

            sgst = round(
                total_tax - cgst,
                2
            )

            igst = 0

        total = round(
            taxable_total + total_tax,
            2
        )

        return Invoice(

            invoice_number=data.get(
                "invoice_number", ""
            ).strip(),

            invoice_date=data.get(
                "invoice_date", ""
            ),

            due_date=data.get(
                "due_date", ""
            ),

            business_name=data.get(
                "business_name", ""
            ).strip(),

            business_address=data.get(
                "business_address", ""
            ).strip(),

            business_gstin=business_gstin,

            customer_name=data.get(
                "customer_name", ""
            ).strip(),

            customer_address=data.get(
                "customer_address", ""
            ).strip(),

            customer_gstin=customer_gstin,

            supplier_state_code=supplier_state_code,

            customer_state_code=customer_state_code,

            place_of_supply=GST_STATE_CODES.get(
                customer_state_code,
                customer_state_code
            ),

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

        return Invoice(

            invoice_number=data.get(
                "invoice_number", ""
            ).strip(),

            invoice_date=data.get(
                "invoice_date", ""
            ),

            due_date=data.get(
                "due_date", ""
            ),

            business_name=data.get(
                "business_name", ""
            ).strip(),

            business_address=data.get(
                "business_address", ""
            ).strip(),

            business_gstin=business_gstin,

            customer_name=data.get(
                "customer_name", ""
            ).strip(),

            customer_address=data.get(
                "customer_address", ""
            ).strip(),

            customer_gstin=customer_gstin,

            supplier_state_code=supplier_state_code,

            customer_state_code=customer_state_code,

            place_of_supply=GST_STATE_CODES.get(
                customer_state_code,
                customer_state_code
            ),

            items=items,

            subtotal=round(subtotal, 2),

            discount=round(discount, 2),

            cgst=cgst,
            sgst=sgst,
            igst=igst,

            total_tax=total_tax,

            total=total
        )