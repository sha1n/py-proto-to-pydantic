from fastapi import APIRouter, Depends
from google.protobuf.json_format import MessageToJson

from generated.proto.webapp.api.message_pb2 import Message  # type: ignore

router = APIRouter()

JSONString = str


def get_message() -> str:
    return "Hello World"


@router.get("/")
async def root(msg=Depends(get_message)) -> JSONString:
    message = Message(
        content=msg,
    )
    return MessageToJson(
        message=message,
        float_precision=2,
    )
