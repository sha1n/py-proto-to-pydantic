import pytest
from google.protobuf.json_format import Parse, MessageToJson

from webapp.api.generated.message_service_pb2 import Message, Sender
from tests.conftest import ITContext


@pytest.mark.it
def test_http_echo(context: ITContext):
    message = Message(
        content=context.faker.sentence(),
        sender=Sender(
            name=context.faker.name(),
            email=context.faker.email(),
        ),
    )

    response = context.client.post(
        url="/echo",
        auth=context.basic_auth,
        json=MessageToJson(
            message=message,
            float_precision=2,
        ),
    )
    actual_message = Parse(text=response.text, message=Message())

    assert response.status_code == 200
    assert actual_message == message
