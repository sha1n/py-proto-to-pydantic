import logging

from fastapi import FastAPI

from myapp.controllers import root_controller

app = FastAPI()

app.include_router(root_controller.router)


@app.on_event("startup")
async def bootstrap():
    logging.info("Starting up...")
