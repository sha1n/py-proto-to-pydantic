from webapp.api.generated.message_service_pb2 import PostMessageRequest, PostMessageResponse
from webapp.api.generated.message_service_pb2_grpc import MessageServiceServicer


class MessageService(MessageServiceServicer):
    def PostMessage(self, request: PostMessageRequest, context) -> PostMessageResponse:
        return PostMessageResponse(message=request.message)
