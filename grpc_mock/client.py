"""
gRPC Echo Client
调用 Echo 服务并打印响应中的 received_metadata，用于验证 header 传递
"""

import sys
import os
import json

import grpc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import echo_pb2
import echo_pb2_grpc


def call_echo(target="127.0.0.1:19090", message="hello", metadata=None):
    channel = grpc.insecure_channel(target)
    stub = echo_pb2_grpc.EchoServiceStub(channel)

    md = []
    if metadata:
        for k, v in metadata.items():
            md.append((k, v))

    response = stub.Echo(echo_pb2.EchoRequest(message=message), metadata=md)

    result = {
        "message": response.message,
        "received_metadata": dict(response.received_metadata),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    channel.close()
    return result


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1:19090"
    message = sys.argv[2] if len(sys.argv) > 2 else "hello"
    call_echo(target, message)
