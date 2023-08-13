from fastapi import APIRouter, Depends
from google.protobuf.json_format import MessageToJson

from webapp.controllers.types import JSONString
from generated.proto.webapp.api.message_pb2 import Message

router = APIRouter()


def get_message() -> str:
    return "Hello World"


@router.get("/")
async def root(msg=Depends(get_message)) -> JSONString:
    message = Message(
        content=msg,
    )
    return MessageToJson(message=message)
