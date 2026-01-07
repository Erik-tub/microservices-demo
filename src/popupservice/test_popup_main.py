import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

mock_grpc = MagicMock()
mock_grpc.insecure_channel = MagicMock(return_value=MagicMock())
mock_grpc.RpcError = Exception

class MockPopupServiceServicer:
    pass

mock_popup_pb2_grpc = MagicMock()
mock_popup_pb2_grpc.PopupServiceServicer = MockPopupServiceServicer

sys.modules['grpc'] = mock_grpc
sys.modules['popup_pb2'] = MagicMock()
sys.modules['popup_pb2_grpc'] = mock_popup_pb2_grpc
sys.modules['demo_pb2'] = MagicMock()
sys.modules['demo_pb2_grpc'] = MagicMock()
sys.modules['grpc_health'] = MagicMock()
sys.modules['grpc_health.v1'] = MagicMock()
sys.modules['grpc_health.v1.health_pb2'] = MagicMock()
sys.modules['grpc_health.v1.health_pb2_grpc'] = MagicMock()
sys.modules['grpc_health.v1.health'] = MagicMock()
sys.modules['opentelemetry'] = MagicMock()
sys.modules['opentelemetry.trace'] = MagicMock()
sys.modules['opentelemetry.sdk'] = MagicMock()
sys.modules['opentelemetry.sdk.trace'] = MagicMock()
sys.modules['opentelemetry.sdk.trace.export'] = MagicMock()
sys.modules['opentelemetry.exporter'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.grpc'] = MagicMock()
sys.modules['opentelemetry.exporter.otlp.proto.grpc.trace_exporter'] = MagicMock()
sys.modules['opentelemetry.instrumentation'] = MagicMock()
sys.modules['opentelemetry.instrumentation.grpc'] = MagicMock()
sys.modules['opentelemetry.sdk.resources'] = MagicMock()

import popup_main


class TestPopupServiceFunctions(unittest.TestCase):
    """Test standalone functions without needing to instantiate the service"""

    def test_get_fallback_outfit(self):
        """Test that fallback outfit returns expected items"""
        service = object.__new__(popup_main.PopupServiceServicer)
        result = service._get_fallback_outfit()
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['id'], 'OLJCESPC7Z')
        self.assertEqual(result[0]['name'], 'Sunglasses')
        self.assertEqual(result[0]['slug'], 'sunglasses')
        self.assertEqual(result[1]['id'], '2ZYFJ3GM2N')
        self.assertEqual(result[1]['name'], 'Tank Top')
        self.assertEqual(result[2]['id'], '66VCHSJNUP')

    def test_select_random_items_with_empty_dict(self):
        """Test select_random_items with empty categories"""
        categories = {}
        result = popup_main.PopupServiceServicer.select_random_items(categories)
        
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)

    def test_select_random_items_with_single_category(self):
        """Test select_random_items with one category"""
        categories = {
            "headwear": [("ID1", "Hat"), ("ID2", "Cap")]
        }
        result = popup_main.PopupServiceServicer.select_random_items(categories)
        
        # The function picks one random item per category
        self.assertEqual(len(result), 1)
        self.assertIn('id', result[0])
        self.assertIn('name', result[0])
        self.assertIn('slug', result[0])

    def test_select_random_items_with_multiple_categories(self):
        """Test select_random_items with multiple categories"""
        categories = {
            "headwear": [("ID1", "Hat"), ("ID2", "Cap")],
            "tops": [("ID3", "Shirt"), ("ID4", "Jacket")],
            "shoes": [("ID5", "Sneakers")]
        }
        result = popup_main.PopupServiceServicer.select_random_items(categories)
        
        # The function picks one item per category
        self.assertEqual(len(result), 3)
        
        for item in result:
            self.assertIsInstance(item, dict)
            self.assertIn('id', item)
            self.assertIn('name', item)
            self.assertIn('slug', item)
            self.assertNotIn(' ', item['slug'])

    def test_select_random_items_with_empty_category(self):
        """Test select_random_items when one category is empty"""
        categories = {
            "headwear": [("ID1", "Hat")],
            "tops": [],
            "shoes": [("ID5", "Sneakers")]
        }
        
        result = popup_main.PopupServiceServicer.select_random_items(categories)
        
        # Should only return items from non-empty categories
        self.assertEqual(len(result), 2)


class TestInitTracing(unittest.TestCase):
    """Test cases for init_tracing function"""

    @patch.dict(os.environ, {'ENABLE_TRACING': '0'})
    @patch('popup_main.logger')
    def test_init_tracing_disabled(self, mock_logger):
        """Test that tracing is skipped when disabled"""
        popup_main.init_tracing()
        mock_logger.info.assert_called_with("Tracing disabled")

    @patch.dict(os.environ, {'ENABLE_TRACING': '1', 'JAEGER_OTLP_ENDPOINT': 'test:4317'})
    @patch('popup_main.trace')
    @patch('popup_main.TracerProvider')
    @patch('popup_main.OTLPSpanExporter')
    @patch('popup_main.BatchSpanProcessor')
    @patch('popup_main.Resource')
    def test_init_tracing_enabled(self, mock_resource, mock_processor, mock_exporter, mock_provider, mock_trace):
        """Test that tracing is initialized when enabled"""
        popup_main.init_tracing()
        
        mock_resource.create.assert_called_once()
        mock_exporter.assert_called_once()
        mock_processor.assert_called_once()


class TestCategoryKeywords(unittest.TestCase):
    """Test category keywords constant"""

    def test_category_keywords_structure(self):
        """Test that CATEGORY_KEYWORDS has expected structure"""
        self.assertIn('headwear', popup_main.CATEGORY_KEYWORDS)
        self.assertIn('tops', popup_main.CATEGORY_KEYWORDS)
        self.assertIn('shoes', popup_main.CATEGORY_KEYWORDS)
        
        self.assertIsInstance(popup_main.CATEGORY_KEYWORDS['headwear'], list)
        self.assertGreater(len(popup_main.CATEGORY_KEYWORDS['headwear']), 0)


if __name__ == '__main__':
    unittest.main()