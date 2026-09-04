import re


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_login(email, password):

    email = email.strip()

    if not email:
        return "Email is required."

    if not EMAIL_PATTERN.match(email):
        return "Please enter a valid email address."

    if not password:
        return "Password is required."

    return None


def validate_registration(
    name,
    email,
    password,
    confirm_password
):

    name = name.strip()
    email = email.strip()

    if not name:
        return "Name is required."

    if len(name) > 100:
        return "Name must be 100 characters or less."

    if not email:
        return "Email is required."

    if not EMAIL_PATTERN.match(email):
        return "Please enter a valid email address."

    if not password:
        return "Password is required."

    if len(password) < 8:
        return "Password must be at least 8 characters."

    if password != confirm_password:
        return "Passwords do not match."

    return None