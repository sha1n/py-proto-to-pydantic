from fastapi import APIRouter
from google.protobuf.json_format import MessageToJson, Parse
from starlette.requests import Request

from webapp.controllers.types import JSONString
from generated.proto.webapp.api.message_pb2 import Message

router = APIRouter()


@router.post("/echo")
async def echo(request: Request) -> JSONString:
    message = Parse(
        text=await request.json(),
        message=Message(),
    )

    return MessageToJson(
        message=message,
        float_precision=2,
    )
