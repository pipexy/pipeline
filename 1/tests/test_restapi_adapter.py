# tests/test_restapi_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import json
import requests

# Import the adapter to test
sys.path.append('..')
from adapters.RESTAdapter import RESTAdapter


class RESTAdapterTest(unittest.TestCase):
    def setUp(self):
        # Sample API response data
        self.sample_users_response = {
            "data": [
                {"id": 1, "name": "John", "email": "john@example.com"},
                {"id": 2, "name": "Jane", "email": "jane@example.com"}
            ]
        }

        self.sample_post_response = {
            "id": 3,
            "name": "New User",
            "email": "new@example.com",
            "created_at": "2023-01-01T00:00:00Z"
        }

        # Config with base URL
        self.config = {
            "base_url": "https://api.example.com",
            "timeout": 30,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        }

    @patch('requests.get')
    def test_get_request(self, mock_get):
        """Test making a GET request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_users_response
        mock_get.return_value = mock_response

        # Create adapter and make request
        adapter = RESTAdapter(self.config)
        adapter.get("/users")
        result = adapter.execute()

        # Verify request and response
        mock_get.assert_called_once_with(
            "https://api.example.com/users",
            headers=self.config["headers"],
            timeout=30,
            params=None
        )

        self.assertEqual(result, self.sample_users_response)
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["name"], "John")

    @patch('requests.get')
    def test_get_with_parameters(self, mock_get):
        """Test GET request with query parameters"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [self.sample_users_response["data"][0]]}
        mock_get.return_value = mock_response

        # Parameters to send
        params = {"id": 1}

        # Create adapter and make request
        adapter = RESTAdapter(self.config)
        adapter.get("/users", params)
        result = adapter.execute()

        # Verify request and response
        mock_get.assert_called_once_with(
            "https://api.example.com/users",
            headers=self.config["headers"],
            timeout=30,
            params=params
        )

        self.assertEqual(result["data"][0]["id"], 1)

    @patch('requests.post')
    def test_post_request(self, mock_post):
        """Test making a POST request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = self.sample_post_response
        mock_post.return_value = mock_response

        # Data to send
        post_data = {
            "name": "New User",
            "email": "new@example.com"
        }

        # Create adapter and make request
        adapter = RESTAdapter(self.config)
        adapter.post("/users", post_data)
        result = adapter.execute()

        # Verify request and response
        mock_post.assert_called_once_with(
            "https://api.example.com/users",
            headers=self.config["headers"],
            timeout=30,
            json=post_data
        )

        self.assertEqual(result["id"], 3)
        self.assertEqual(result["name"], "New User")

    @patch('requests.put')
    def test_put_request(self, mock_put):
        """Test making a PUT request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "Updated User",
            "email": "john@example.com"
        }
        mock_put.return_value = mock_response

        # Data to send
        put_data = {
            "name": "Updated User"
        }

        # Create adapter and make request
        adapter = RESTAdapter(self.config)
        adapter.put("/users/1", put_data)
        result = adapter.execute()

        # Verify request and response
        mock_put.assert_called_once_with(
            "https://api.example.com/users/1",
            headers=self.config["headers"],
            timeout=30,
            json=put_data
        )

        self.assertEqual(result["name"], "Updated User")

    @patch('requests.delete')
    def test_delete_request(self, mock_delete):
        """Test making a DELETE request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_delete.return_value = mock_response

        # Create adapter and make request
        adapter = RESTAdapter(self.config)
        adapter.delete("/users/1")
        result = adapter.execute()

        # Verify request
        mock_delete.assert_called_once_with(
            "https://api.example.com/users/1",
            headers=self.config["headers"],
            timeout=30
        )

        # For DELETE with 204, we expect None or empty result
        self.assertIsNone(result)

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """Test handling HTTP error responses"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "User not found"}
        mock_get.return_value = mock_response

        # Create adapter and make request
        adapter = RESTAdapter(self.config)
        adapter.get("/users/999")

        # Should raise an exception
        with self.assertRaises(Exception) as context:
            adapter.execute()

        self.assertIn("404", str(context.exception))

    @patch('requests.get')
    def test_custom_headers(self, mock_get):
        """Test sending custom headers"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_users_response
        mock_get.return_value = mock_response

        # Custom headers
        custom_headers = {
            "Authorization": "Bearer token123",
            "X-API-Key": "abc123"
        }

        # Create adapter with base headers, then add custom ones
        adapter = RESTAdapter(self.config)
        adapter.set_headers(custom_headers)
        adapter.get("/users")
        adapter.execute()

        # Verify headers were merged
        expected_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer token123",
            "X-API-Key": "abc123"
        }

        # Get the headers from the mock call
        called_headers = mock_get.call_args[1]["headers"]

        # Verify all expected headers are present
        for key, value in expected_headers.items():
            self.assertEqual(called_headers[key], value)

    @patch('requests.get')
    def test_json_parsing(self, mock_get):
        """Test parsing JSON response"""
        # Mock response with different content types
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = self.sample_users_response
        mock_get.return_value = mock_response

        # Create adapter and make request
        adapter = RESTAdapter(self.config)
        adapter.get("/users")
        result = adapter.execute()

        # Verify JSON was parsed
        self.assertIsInstance(result, dict)
        self.assertIn("data", result)

    @patch('requests.get')
    def test_retry_mechanism(self, mock_get):
        """Test retry mechanism for failed requests"""
        # Configure adapter with retries
        retry_config = self.config.copy()
        retry_config["max_retries"] = 3
        retry_config["retry_delay"] = 0  # No delay for test

        # First call fails, second succeeds
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),
            MagicMock(status_code=200, json=lambda: self.sample_users_response)
        ]

        # Create adapter and make request
        adapter = RESTAdapter(retry_config)
        adapter.get("/users")
        result = adapter.execute()

        # Verify retry worked and we got the result
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(result["data"][0]["name"], "John")

    @patch('requests.post')
    def test_file_upload(self, mock_post):
        """Test file upload functionality"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "file123", "name": "test.txt"}
        mock_post.return_value = mock_response

        # Create adapter
        adapter = RESTAdapter(self.config)

        # Prepare test file content
        file_content = b"Test file content"

        # Call upload method
        adapter.upload_file("/files", "test.txt", file_content, "text/plain")
        result = adapter.execute()

        # Verify the request
        self.assertTrue(mock_post.called)

        # Check the right endpoint was called
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.example.com/files")

        # Verify we got back the upload result
        self.assertEqual(result["id"], "file123")
        self.assertEqual(result["name"], "test.txt")


if __name__ == "__main__":
    unittest.main()
