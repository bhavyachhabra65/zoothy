from decimal import Decimal, InvalidOperation


VALID_MOVEMENT_TYPES = {"add", "remove"}


def validate_stock_adjustment(
    movement_type,
    quantity,
    reason,
    low_stock_level
):

    movement_type = (movement_type or "").strip().lower()
    quantity = (quantity or "").strip()
    reason = (reason or "").strip()
    low_stock_level = (low_stock_level or "0").strip()

    if movement_type not in VALID_MOVEMENT_TYPES:
        return "Select a valid stock action."

    try:
        quantity_value = Decimal(quantity)
    except (InvalidOperation, ValueError):
        return "Enter a valid quantity."

    if quantity_value <= 0:
        return "Quantity must be greater than zero."

    if quantity_value.as_tuple().exponent < -3:
        return "Quantity can have up to 3 decimal places."

    try:
        low_stock_value = Decimal(low_stock_level or "0")
    except (InvalidOperation, ValueError):
        return "Enter a valid low-stock level."

    if low_stock_value < 0:
        return "Low-stock level cannot be negative."

    if low_stock_value.as_tuple().exponent < -3:
        return "Low-stock level can have up to 3 decimal places."

    if len(reason) > 255:
        return "Reason cannot be longer than 255 characters."

    if not reason:
        return "Reason is required."

    return None


def validate_low_stock_level(low_stock_level):

    value = (low_stock_level or "0").strip()

    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError):
        return "Enter a valid low-stock level."

    if number < 0:
        return "Low-stock level cannot be negative."

    if number.as_tuple().exponent < -3:
        return "Low-stock level can have up to 3 decimal places."

    return None
