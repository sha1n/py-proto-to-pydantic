import os

from webapp.security.basic_auth_middleware import UserCredentials


def get_basic_auth_username() -> str:
    return os.getenv("BASIC_AUTH_USERNAME")


def get_basic_auth_password() -> str:
    return os.getenv("BASIC_AUTH_PASSWORD")


def get_basic_auth_credentials() -> UserCredentials:
    return UserCredentials(username=get_basic_auth_username(), password=get_basic_auth_password())