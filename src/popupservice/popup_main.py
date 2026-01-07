from concurrent import futures
import os
import grpc
import time
import json
import random
import logging
import sys

import popup_pb2
import popup_pb2_grpc
import demo_pb2
import demo_pb2_grpc

from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.sdk.resources import Resource



logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "severity": "%(levelname)s", "message": "%(message)s", "service": "popupservice"}',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


CATEGORY_KEYWORDS = {
    "headwear": ['hat', 'cap', 'beanie', 'helmet', 'headband', 'visor', 'glasses'],
    "tops": ['shirt', 'tank', 'blouse', 'sweater', 'jacket', 'hoodie', 'top', 'tee', 'watch'],
    "shoes": ['shoes', 'boots', 'sneakers', 'loafers', 'sandals', 'slippers', 'heels']
}
    
class PopupServiceServicer(popup_pb2_grpc.PopupServiceServicer):
    def __init__(self):
        catalog_addr = os.getenv("PRODUCT_CATALOG_SERVICE_ADDR", "productcatalogservice:3550")
        logger.info(f"Connecting to product catalog service at {catalog_addr}")

        self.catalog_channel = grpc.insecure_channel(catalog_addr)
        self.catalog_stub = demo_pb2_grpc.ProductCatalogServiceStub(self.catalog_channel)

    def select_random_items(self, categories_dict, max_items=3):
        recommended = []
        # Flatten all products into a single list with category info
        all_products = []
        for cat, items in categories_dict.items():
            all_products.extend(items)
        
        # Randomly select up to max_items
        selected = random.sample(all_products, min(max_items, len(all_products)))
        
        # Convert to dict format
        for product_id, product_name in selected:
            recommended.append({
                "id": product_id,
                "name": product_name,
                "slug": product_name.lower().replace(" ", "-")
            })

        return recommended

            


    def select_random_items(categories_dict):
        recommended = []
        for cat, items in categories_dict.items():
            if items: 
                product_id, product_name = random.choice(items)
                recommended.append({
                    "id": product_id,
                    "name": product_name,
                    "slug": product_name.lower().replace(" ", "-")
                })
            
        return recommended
            
    def MakeOutfitRecommendation(self):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("make_outfit_recommendation"):
            try:
                logger.debug("Fetching products from catalog service")
                products_response = self.catalog_stub.ListProducts(demo_pb2.Empty())
                categories_dict = self.categorize_products(products_response.products)
                recommended = self.select_random_items(categories_dict, max_items=3)


                logger.info("Categorized products - " + ", ".join(f"{cat}: {len(items)}" for cat, items in categories_dict.items()))

                if len(recommended) == len(CATEGORY_KEYWORDS):
                    logger.info(f"Successfully created outfit recommendation with {len(recommended)} items")
                    return recommended
                else:
                    logger.warning(f"Could only find {len(recommended)} items, using fallback")
                    return self._get_fallback_outfit()

            except grpc.RpcError as e:
                logger.error(f"gRPC error while fetching products: {e.code()} - {e.details()}")
                return self._get_fallback_outfit()
            except Exception as e:
                logger.error(f"Unexpected error in MakeOutfitRecommendation: {str(e)}")
                return self._get_fallback_outfit()

    def _get_fallback_outfit(self):
        return [
            {'id': 'OLJCESPC7Z', 'name': 'Sunglasses', 'slug': 'sunglasses'},
            {'id': '2ZYFJ3GM2N', 'name': 'Tank Top', 'slug': 'tank-top'},
            {'id': '66VCHSJNUP', 'name': 'Loafers', 'slug': 'loafers'}
        ]

    def GetPopupMessage(self, request, context):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("get_popup_message") as span:
            session_id = request.session_id or "unknown"
            span.set_attribute("session.id", session_id)
            logger.info(f"Popup message requested for session: {session_id}")

            try:
                recommended = self.MakeOutfitRecommendation()
                data = {"items": recommended}
                logger.info(f"Returning outfit recommendation for session: {session_id}")
                return popup_pb2.PopupReply(message=json.dumps(data))
            except Exception as e:
                logger.error(f"Error in GetPopupMessage: {str(e)}")
                data = {"items": self._get_fallback_outfit()}
                return popup_pb2.PopupReply(message=json.dumps(data))


def init_tracing():
    if os.getenv("ENABLE_TRACING") != "1":
        logger.info("Tracing disabled")
        return

    logger.info("Initializing OTLP tracing to Jaeger")
    jaeger_endpoint = os.getenv("JAEGER_OTLP_ENDPOINT", "jaeger:4317")

    resource = Resource.create({"service.name": "popupservice"})
    trace.set_tracer_provider(TracerProvider(resource=resource))

    otlp_exporter = OTLPSpanExporter(
        endpoint=jaeger_endpoint,
        insecure=True
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    logger.info(f"Tracing configured with OTLP endpoint at {jaeger_endpoint}")


def serve():
    init_tracing()

    port = os.getenv("PORT", "8080")
    if os.getenv("ENABLE_TRACING") == "1":
        GrpcInstrumentorServer().instrument()
        from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
        GrpcInstrumentorClient().instrument()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    popup_pb2_grpc.add_PopupServiceServicer_to_server(PopupServiceServicer(), server)

    health_servicer = HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set("popupservice", health_pb2.HealthCheckResponse.SERVING)

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"popupservice listening on port {port}")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down popupservice")
        server.stop(0)


if __name__ == "__main__":
    serve()
