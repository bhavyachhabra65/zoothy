from decimal import Decimal, InvalidOperation


def validate_product(
    name,
    sku,
    hsn_sac,
    unit,
    purchase_price,
    selling_price,
    gst_rate,
    description
):

    name = (name or "").strip()
    sku = (sku or "").strip()
    hsn_sac = (hsn_sac or "").strip().upper()
    unit = (unit or "").strip()
    purchase_price = (purchase_price or "").strip()
    selling_price = (selling_price or "").strip()
    gst_rate = (gst_rate or "").strip()

    if not name:
        return "Product name is required."

    if len(name) > 150:
        return "Product name cannot be longer than 150 characters."

    if len(sku) > 100:
        return "SKU cannot be longer than 100 characters."

    if len(hsn_sac) > 20:
        return "HSN / SAC cannot be longer than 20 characters."

    if not unit:
        return "Unit is required."

    if len(unit) > 30:
        return "Unit cannot be longer than 30 characters."

    for value, label in (
        (purchase_price, "Purchase price"),
        (selling_price, "Selling price"),
        (gst_rate, "GST rate")
    ):
        try:
            number = Decimal(value or "0")
        except (InvalidOperation, ValueError):
            return f"Enter a valid {label.lower()}."

        if number < 0:
            return f"{label} cannot be negative."

    try:
        gst = Decimal(gst_rate or "0")
    except (InvalidOperation, ValueError):
        return "Enter a valid GST rate."

    allowed_gst_rates = {Decimal("0"), Decimal("5"), Decimal("12"), Decimal("18"), Decimal("28")}
    if gst not in allowed_gst_rates:
        return "Select a valid GST rate: 0%, 5%, 12%, 18% or 28%."

    return None
