from fastapi import APIRouter
from google.protobuf.json_format import Parse, MessageToDict
from starlette.requests import Request

from webapp.api.generated.message_service_pb2 import Message

router = APIRouter()


@router.post("/echo")
async def echo(request: Request) -> dict:
    message = Parse(
        text=await request.json(),
        message=Message(),
    )

    return MessageToDict(
        message=message,
        float_precision=2,
    )
