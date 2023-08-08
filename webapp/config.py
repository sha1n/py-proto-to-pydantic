import os


def get_basic_auth_username() -> str:
    return os.getenv("BASIC_AUTH_USERNAME")


def get_basic_auth_password() -> str:
    return os.getenv("BASIC_AUTH_PASSWORD")
