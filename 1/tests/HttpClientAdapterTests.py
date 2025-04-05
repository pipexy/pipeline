# tests/test_http_client_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import json

# Import the adapter to test
sys.path.append('..')
from adapters.HttpClientAdapter import HttpClientAdapter


class HttpClientAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test environment
        self.test_url = "https://api.example.com/test"
        self.test_response = {
            "status": "success",
            "data": {"id": 1, "name": "Test"}
        }

    def test_initialization(self):
        """Test basic initialization of HttpClientAdapter"""
        adapter = HttpClientAdapter({})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, {})

    @patch('requests.get')
    def test_get_request(self, mock_get):
        """Test executing a GET request"""
        # Mock the requests.get return value
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.test_response
        mock_resp.status_code = 200
        mock_resp.text = json.dumps(self.test_response)
        mock_get.return_value = mock_resp

        adapter = HttpClientAdapter({})
        adapter.url(self.test_url)
        adapter.method("GET")
        result = adapter.execute()

        # Verify the request was made
        mock_get.assert_called_once_with(self.test_url, headers={}, params={}, timeout=30)
        self.assertEqual(result, self.test_response)

    @patch('requests.post')
    def test_post_request(self, mock_post):
        """Test executing a POST request with body"""
        # Mock the requests.post return value
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.test_response
        mock_resp.status_code = 201
        mock_resp.text = json.dumps(self.test_response)
        mock_post.return_value = mock_resp

        test_body = {"name": "New Test"}

        adapter = HttpClientAdapter({})
        adapter.url(self.test_url)
        adapter.method("POST")
        adapter.body(test_body)
        result = adapter.execute()

        # Verify the request was made
        mock_post.assert_called_once_with(
            self.test_url,
            headers={'Content-Type': 'application/json'},
            json=test_body,
            data=None,
            timeout=30
        )
        self.assertEqual(result, self.test_response)

    @patch('requests.get')
    def test_headers(self, mock_get):
        """Test setting custom headers"""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.test_response
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        test_headers = {
            "Authorization": "Bearer token123",
            "X-Custom-Header": "custom-value"
        }

        adapter = HttpClientAdapter({})
        adapter.url(self.test_url)
        adapter.headers(test_headers)
        adapter.execute()

        # Verify headers were set correctly
        mock_get.assert_called_once()
        called_headers = mock_get.call_args[1]['headers']
        self.assertEqual(called_headers.get("Authorization"), "Bearer token123")
        self.assertEqual(called_headers.get("X-Custom-Header"), "custom-value")

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """Test handling of HTTP errors"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("404 Client Error")
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        adapter = HttpClientAdapter({})
        adapter.url(self.test_url)

        with self.assertRaises(Exception):
            adapter.execute()


if __name__ == "__main__":
    unittest.main()