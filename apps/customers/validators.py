import re


_EMAIL_PATTERN = re.compile(
    r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
)

_GSTIN_PATTERN = re.compile(
    r"^[0-9A-Z]{15}$"
)


def validate_customer(
    name,
    phone,
    email,
    gstin,
    address,
    notes
):

    name = (name or "").strip()
    phone = (phone or "").strip()
    email = (email or "").strip()
    gstin = (gstin or "").strip().upper()

    if not name:
        return "Customer name is required."

    if len(name) > 150:
        return "Customer name cannot be longer than 150 characters."

    if phone and (not phone.isdigit() or len(phone) != 10):
        return "Enter a valid 10-digit phone number."

    if email and not _EMAIL_PATTERN.fullmatch(email):
        return "Enter a valid email address."

    if gstin and not _GSTIN_PATTERN.fullmatch(gstin):
        return "GSTIN must contain 15 letters and numbers."

    return None
