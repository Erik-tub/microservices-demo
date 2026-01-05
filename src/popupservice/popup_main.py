from concurrent import futures
import os
import grpc
import time
import json
import random

import popup_pb2
import popup_pb2_grpc


import demo_pb2
import demo_pb2_grpc


class PopupServiceServicer(popup_pb2_grpc.PopupServiceServicer):
    def __init__(self):
        catalog_addr = os.getenv("PRODUCT_CATALOG_SERVICE_ADDR", "productcatalogservice:3550")
        self.catalog_channel = grpc.insecure_channel(catalog_addr)
        self.catalog_stub = demo_pb2_grpc.ProductCatalogServiceStub(self.catalog_channel)

    def MakeOutfitRecommendation(self):
        try:
            products_response = self.catalog_stub.ListProducts(demo_pb2.Empty())
            headwear_keywords = ['hat', 'cap', 'beanie', 'helmet', 'headband', 'visor', 'glasses']
            top_keywords = ['shirt', 'tank', 'blouse', 'sweater', 'jacket', 'hoodie', 'top', 'tee', 'watch']
            shoes_keywords = ['shoes', 'boots', 'sneakers', 'loafers', 'sandals', 'slippers', 'heels']
            headwear = []
            tops = []
            shoes = []
            for product in products_response.products:
                name_lower = product.name.lower()
                if any(keyword in name_lower for keyword in headwear_keywords):
                    headwear.append(product.name)
                elif any(keyword in name_lower for keyword in top_keywords):
                    tops.append(product.name)
                elif any(keyword in name_lower for keyword in shoes_keywords):
                    shoes.append(product.name)
            recommended = []
            if headwear:
                recommended.append(random.choice(headwear).lower().replace(' ', '-'))
            if tops:
                recommended.append(random.choice(tops).lower().replace(' ', '-'))
            if shoes:
                recommended.append(random.choice(shoes).lower().replace(' ', '-'))

            return recommended if len(recommended) == 3 else ["sunglasses", "tank-top", "loafers"]

        except grpc.RpcError:
            return ["sunglasses", "tank-top", "loafers"]

    def GetPopupMessage(self, request, context):
        try:
            products_response = self.catalog_stub.ListProducts(demo_pb2.Empty())
            product_names = [p.name for p in products_response.products]
            product_text = ", ".join(product_names[:10])
            recommended = self.MakeOutfitRecommendation()

            data = {
                "image": f"/static/img/products/{recommended[0]}.jpg",
                "image2": f"/static/img/products/{recommended[1]}.jpg",
                "image3": f"/static/img/products/{recommended[2]}.jpg",
                "text": f"Recommended outfit: {', '.join(recommended)}"
            }
            return popup_pb2.PopupReply(message=json.dumps(data))
        except grpc.RpcError as e:
            data = {
                "image": "/static/img/products/sunglasses.jpg",
                "image2": "/static/img/products/tank-top.jpg",
                "image3": "/static/img/products/loafers.jpg",
                "text": "Product catalog unavailable"
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
