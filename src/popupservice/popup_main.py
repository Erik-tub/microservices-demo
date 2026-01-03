from concurrent import futures
import os
import grpc
import time

import popup_pb2
import popup_pb2_grpc

class PopupServiceServicer(popup_pb2_grpc.PopupServiceServicer):
    def GetPopupMessage(self, request, context):
        # Gib einen JSON-String mit Bild-URL und Text zurück
        import json
        data = {
            "image": "/static/img/products/sunglasses.jpg",
            "image2": "/static/img/products/tank-top.jpg",
            "image3": "/static/img/products/loafers.jpg",
            "text": "Head: sunglasses, Body: tank-top, Shoes: loafers"
        }
        return popup_pb2.PopupReply(message=json.dumps(data))

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
