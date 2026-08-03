from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass(slots=True)
class ChequeData:
    bank: str
    cheque_date: date
    pay_to: str
    amount: Decimal
    amount_in_words: str
    ac_payee_only: bool

    @property
    def formatted_date(self) -> str:
        return "\u00A0\u00A0".join(self.cheque_date.strftime("%d%m%Y"))