import re


def validate_business_settings(
    business_name,
    phone,
    gstin,
    address
):

    business_name = business_name.strip()
    phone = phone.strip()
    gstin = gstin.strip().upper()
    address = address.strip()

    if not business_name:
        return "Business name is required."

    if len(business_name) > 150:
        return "Business name is too long."

    if phone:

        if not re.fullmatch(
            r"[6-9]\d{9}",
            phone
        ):
            return "Enter a valid 10-digit mobile number."

    if gstin:

        if not re.fullmatch(
            r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]",
            gstin
        ):
            return "Enter a valid GSTIN."

    return None