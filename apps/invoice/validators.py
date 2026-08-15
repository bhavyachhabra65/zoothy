import re
from decimal import Decimal


class ValidationError(Exception):
    pass


GSTIN_PATTERN = re.compile(
    r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"
)


def validate_gstin(gstin, field_name):

    gstin = gstin.strip().upper()

    if not GSTIN_PATTERN.fullmatch(gstin):
        raise ValidationError(
            f"{field_name} must be a valid GSTIN."
        )


def validate_invoice(data):

    if not data.invoice_number.strip():
        raise ValidationError(
            "Invoice Number is required."
        )

    if not data.invoice_date:
        raise ValidationError(
            "Invoice Date is required."
        )

    if not data.business_name.strip():
        raise ValidationError(
            "Business Name is required."
        )

    if not data.business_address.strip():
        raise ValidationError(
            "Business Address is required."
        )

    validate_gstin(
        data.business_gstin,
        "Business GSTIN"
    )

    if not data.customer_name.strip():
        raise ValidationError(
            "Customer Name is required."
        )

    if not data.customer_address.strip():
        raise ValidationError(
            "Customer Address is required."
        )

    validate_gstin(
        data.customer_gstin,
        "Customer GSTIN"
    )

    if not data.items:
        raise ValidationError(
            "At least one item is required."
        )

    for index, item in enumerate(data.items, start=1):

        if not item.name.strip():
            raise ValidationError(
                f"Item {index}: Product / Service is required."
            )

        if item.quantity <= 0:
            raise ValidationError(
                f"Item {index}: Quantity must be greater than zero."
            )

        if item.price < 0:
            raise ValidationError(
                f"Item {index}: Price cannot be negative."
            )

        if item.gst_rate < 0:
            raise ValidationError(
                f"Item {index}: GST cannot be negative."
            )

    if data.discount < 0:
        raise ValidationError(
            "Discount cannot be negative."
        )