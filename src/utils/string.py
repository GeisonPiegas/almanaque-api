from django.utils.crypto import get_random_string


def generate_random(length: int = 11, allowed_chars: str | None = None):
    if not allowed_chars:
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return get_random_string(length, allowed_chars=allowed_chars)
