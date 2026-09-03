from decimal import Decimal


def format_quantity(value):
    if value is None:
        return "0"

    try:
        quantity = Decimal(str(value))
    except (ValueError, TypeError):
        return str(value)

    if quantity == quantity.to_integral_value():
        return f"{quantity:.0f}"

    return f"{quantity:.3f}".rstrip("0").rstrip(".")


def register_template_filters(app):
    app.jinja_env.filters["format_quantity"] = format_quantity