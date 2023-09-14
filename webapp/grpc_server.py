import logging
from concurrent import futures
from typing import Any

from grpc import server  # type: ignore
from webapp.api.generated.message_service_pb2_grpc import add_MessageServiceServicer_to_server
from webapp.grpc.message_service import MessageService


def serve() -> Any:
    grpcserver = server(futures.ThreadPoolExecutor(max_workers=10))
    add_MessageServiceServicer_to_server(MessageService(), grpcserver)
    grpcserver.add_insecure_port("[::]:50051")
    grpcserver.start()

    return grpcserver


if __name__ == "__main__":
    logging.basicConfig()
    grpc_server = serve()
    grpc_server.wait_for_termination()
