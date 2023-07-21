from fastapi import APIRouter, Depends

from webapp.models.message import Message

router = APIRouter()


def get_message() -> str:
    return "Hello World"


@router.get("/")
async def root(msg=Depends(get_message)) -> Message:
    return Message(message=msg)
