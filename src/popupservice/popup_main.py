from concurrent import futures
import os
import grpc
import time

import popup_pb2
import popup_pb2_grpc

class PopupServiceServicer(popup_pb2_grpc.PopupServiceServicer):
    def GetPopupMessage(self, request, context):
        msg = f"Head: Body: Shoes: "
        return popup_pb2.PopupReply(message=msg)

def serve():
    port = os.getenv("PORT", "8080")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    popup_pb2_grpc.add_PopupServiceServicer_to_server(PopupServiceServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"popupservice listening on port {port}", flush=True)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
