from decimal import Decimal, InvalidOperation


def validate_sale_date(value):
    if not value:
        return "Sale date is required."
    return None


def validate_sale_items(items):
    if not items:
        return "Add at least one product."

    valid_rows = 0

    for item in items:
        if not item.get("product_id"):
            return "Select a product for every row."

        try:
            quantity = Decimal(str(item.get("quantity", "")))
        except (InvalidOperation, ValueError):
            return "Enter a valid quantity."

        if quantity <= 0:
            return "Quantity must be greater than zero."

        try:
            price = Decimal(str(item.get("unit_price", "")))
        except (InvalidOperation, ValueError):
            return "Enter a valid selling price."

        if price < 0:
            return "Selling price cannot be negative."

        valid_rows += 1

    if valid_rows == 0:
        return "Add at least one product."

    return None
