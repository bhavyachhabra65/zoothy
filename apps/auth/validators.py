import re


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

def validate_registration(
    name,
    email,
    password,
    confirm_password
):
    name = name.strip()
    email = email.strip().lower()

    if not name:
        return "Name is required."

    if len(name) > 100:
        return "Name is too long."

    if not EMAIL_PATTERN.fullmatch(email):
        return "Enter a valid email address."

    if len(password) < 8:
        return "Password must be at least 8 characters."

    if password != confirm_password:
        return "Passwords do not match."

    return None


def validate_login(email, password):

    email = email.strip().lower()

    if not email:
        return "Email is required."

    if not password:
        return "Password is required."

    return None