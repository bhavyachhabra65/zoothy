from dataclasses import dataclass


@dataclass
class InvoiceItem:
    name: str
    hsn_code: str
    quantity: float
    price: float
    gst_rate: float
    taxable_amount: float
    discount_amount: float
    tax_amount: float
    amount: float


@dataclass
class Invoice:
    invoice_number: str
    invoice_date: str
    due_date: str

    business_name: str
    business_address: str
    business_gstin: str

    customer_name: str
    customer_address: str
    customer_gstin: str

    vehicle_number: str
    driver_name: str
    route: str
    travel_date: str

    supplier_state_code: str
    customer_state_code: str
    place_of_supply: str

    items: list[InvoiceItem]

    subtotal: float
    discount: float

    cgst: float
    sgst: float
    igst: float

    total_tax: float
    total: float