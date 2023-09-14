import grpc  # type: ignore

from tests.conftest import Faker
from webapp.api.generated.message_service_pb2 import Message, PostMessageRequest, PostMessageResponse, Sender
from webapp.api.generated.message_service_pb2_grpc import MessageServiceStub
from webapp.grpc_server import serve


async def test_post_message(faker: Faker):
    server = serve()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = MessageServiceStub(channel)

        message = Message(content="Hello World!", sender=Sender(name=faker.name(), email=faker.email()))
        response: PostMessageResponse = stub.PostMessage(PostMessageRequest(message=message))

        assert response.message == message

    server.stop(0)
