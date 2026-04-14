import re

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

def is_valid_email(email):
    return re.match(EMAIL_REGEX, email) is not None

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )
    