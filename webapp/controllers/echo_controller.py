from fastapi import APIRouter
from google.protobuf.json_format import MessageToJson, Parse
from starlette.requests import Request

from generated.proto.webapp.api.message_pb2 import Message  # type: ignore

router = APIRouter()

JSONString = str


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
