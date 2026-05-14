"""
Mock gRPC Echo Server
回显所有收到的 metadata（请求头），用于验证 Nginx grpc_set_header 功能
"""

import sys
import os
from concurrent import futures

import grpc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import echo_pb2
import echo_pb2_grpc


class EchoServicer(echo_pb2_grpc.EchoServiceServicer):
    def Echo(self, request, context):
        metadata = dict(context.invocation_metadata())
        return echo_pb2.EchoResponse(
            message=request.message,
            received_metadata=metadata,
        )


def serve(port=19090):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    print(f"gRPC Echo Server started on port {port}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 19090
    serve(port)
