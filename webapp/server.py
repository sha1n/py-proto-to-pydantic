import logging

from fastapi import FastAPI
from starlette.datastructures import URL
from starlette.middleware.authentication import AuthenticationMiddleware

from webapp.config import get_basic_auth_username, get_basic_auth_password
from webapp.auth.auth_check_middleware import AuthenticationCheckMiddleware
from webapp.auth.basic_auth_middleware import BasicAuthBackend
from webapp.controllers import root_controller

app = FastAPI()


async def is_allowed(username: str, password: str) -> bool:
    return username == get_basic_auth_username() and password == get_basic_auth_password()


def is_protected(url: URL):
    return url.path.startswith("/api")


app.include_router(root_controller.router)
app.add_middleware(AuthenticationCheckMiddleware, **{"is_protected": is_protected})
app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend(is_allowed=is_allowed))


@app.on_event("startup")
async def bootstrap():
    logging.info("Starting up...")
