from fastapi import APIRouter

from myapp.models.message import Message

router = APIRouter()


@router.get("/")
async def root() -> Message:
    return Message(message="Hello World")
