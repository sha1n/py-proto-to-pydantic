import logging

from fastapi import FastAPI

from webapp.security.basic_auth_middleware import UserListAccessGuard, add_basic_auth_middleware
from webapp.config import get_basic_auth_credentials
from webapp.controllers import root_controller, echo_controller

app = FastAPI()

app.include_router(root_controller.router)
app.include_router(echo_controller.router)

access_guard = UserListAccessGuard(allowed_users=[get_basic_auth_credentials()])
add_basic_auth_middleware(app=app, access_guard=access_guard)


@app.on_event("startup")
async def bootstrap():
    logging.info("Starting up...")
