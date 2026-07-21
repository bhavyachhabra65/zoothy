from decimal import Decimal


class ValidationError(Exception):
    pass


def validate_cheque(data):

    if not data.bank:
        raise ValidationError("Please select a bank.")

    if not data.pay_to.strip():
        raise ValidationError("Pay To is required.")

    if data.amount <= Decimal("0"):
        raise ValidationError("Amount must be greater than zero.")

    if data.amount.as_tuple().exponent < -2:
        raise ValidationError("Amount can have at most 2 decimal places.")