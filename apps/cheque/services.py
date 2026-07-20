from datetime import datetime
from decimal import Decimal
from num2words import num2words


from .schemas import ChequeData

def build_cheque_data(form):

    return ChequeData(

        bank=form["bank"],

        cheque_date=datetime.strptime(
            form["date"],
            "%Y-%m-%d"
        ).date(),

        pay_to=form["pay_to"].strip(),

        amount=Decimal(form["amount"]),

        amount_in_words=amount_to_words(form["amount"]),

        ac_payee_only=(
            form.get("ac_payee_only") == "on"
        )

    )

def clean_words(words: str) -> str:
    return (
        words.replace(",", "")
             .replace(" and ", " ")
             .replace("-", " ")
             .title()
    )

def amount_to_words(amount: Decimal) -> str:
    amount = Decimal(amount).quantize(Decimal("0.01"))

    rupees = int(amount)
    paise = int((amount - rupees) * 100)

    result = ""

    if rupees > 0:
        result += clean_words(num2words(rupees, lang="en_IN")).title()
        result += " Rupee" if rupees == 1 else " Rupees"

    if paise > 0:
        if result:
            result += " and "

        result += clean_words(num2words(paise, lang="en_IN")).title()
        result += " Paisa" if paise == 1 else " Paise"

    if not result:
        result = "Zero Rupees"

    return result + " Only"