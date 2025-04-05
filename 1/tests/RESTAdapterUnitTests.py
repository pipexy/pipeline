# tests/test_rest_adapter.py
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
        # Setup test config
        self.config = {
            "base_url": "https://api.example.com",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token"
            }
        }

        # Sample response data
        self.sample_response = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com"
        }

    def test_initialization(self):
        """Test basic initialization of RESTAdapter"""
        adapter = RESTAdapter(self.config)
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, self.config)

    @patch('requests.get')
    def test_get_request(self, mock_get):
        """Test making a GET request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_response
        mock_get.return_value = mock_response

        adapter = RESTAdapter(self.config)
        adapter.get("/users/1")
        result = adapter.execute()

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://api.example.com/users/1",
            headers=self.config["headers"],
            params=None
        )

        # Verify the response
        self.assertEqual(result, self.sample_response)

    @patch('requests.post')
    def test_post_request(self, mock_post):
        """Test making a POST request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = self.sample_response
        mock_post.return_value = mock_response

        # Request data
        data = {
            "name": "New User",
            "email": "new@example.com"
        }

        adapter = RESTAdapter(self.config)
        adapter.post("/users", data)
        result = adapter.execute()

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "https://api.example.com/users",
            headers=self.config["headers"],
            json=data
        )

        # Verify the response
        self.assertEqual(result, self.sample_response)

    @patch('requests.put')
    def test_put_request(self, mock_put):
        """Test making a PUT request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "name": "Updated User",
            "email": "updated@example.com"
        }
        mock_put.return_value = mock_response

        # Request data
        data = {
            "name": "Updated User",
            "email": "updated@example.com"
        }

        adapter = RESTAdapter(self.config)
        adapter.put("/users/1", data)
        result = adapter.execute()

        # Verify the request was made correctly
        mock_put.assert_called_once_with(
            "https://api.example.com/users/1",
            headers=self.config["headers"],
            json=data
        )

        # Verify the response
        self.assertEqual(result["name"], "Updated User")

    @patch('requests.delete')
    def test_delete_request(self, mock_delete):
        """Test making a DELETE request"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        adapter = RESTAdapter(self.config)
        adapter.delete("/users/1")
        result = adapter.execute()

        # Verify the request was made correctly
        mock_delete.assert_called_once_with(
            "https://api.example.com/users/1",
            headers=self.config["headers"]
        )

        # For DELETE with no content, result might be None or True
        self.assertTrue(result is None or result is True)

    @patch('requests.get')
    def test_get_with_params(self, mock_get):
        """Test making a GET request with query parameters"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_response]
        mock_get.return_value = mock_response

        # Query parameters
        params = {
            "name": "Test",
            "limit": 10
        }

        adapter = RESTAdapter(self.config)
        adapter.get("/users", params)
        result = adapter.execute()

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://api.example.com/users",
            headers=self.config["headers"],
            params=params
        )

        # Verify the response
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Test User")

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """Test handling HTTP errors"""
        # Mock an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "User not found"}
        mock_get.return_value = mock_response

        adapter = RESTAdapter(self.config)
        adapter.get("/users/999")

        # Should raise an exception
        with self.assertRaises(Exception):
            adapter.execute()

    @patch('requests.get')
    def test_custom_error_handling(self, mock_get):
        """Test custom error handling"""
        # Mock an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "User not found"}
        mock_get.return_value = mock_response

        # Custom config with error_as_response flag
        custom_config = self.config.copy()
        custom_config["error_as_response"] = True

        adapter = RESTAdapter(custom_config)
        adapter.get("/users/999")
        result = adapter.execute()

        # Should return the error response, not raise an exception
        self.assertEqual(result["error"], "User not found")

    @patch('requests.post')
    def test_file_upload(self, mock_post):
        """Test file upload via POST"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "filename": "test.txt"}
        mock_post.return_value = mock_response

        # Create a custom adapter with different Content-Type
        custom_config = self.config.copy()
        custom_config["headers"] = {"Authorization": "Bearer test-token"}

        adapter = RESTAdapter(custom_config)

        # Mock file data
        files = {"file": ("test.txt", "file content")}

        adapter.upload("/upload", files)
        result = adapter.execute()

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        self.assertEqual(call_args["url"], "https://api.example.com/upload")
        self.assertIn("files", call_args)

        # Verify the response
        self.assertEqual(result["filename"], "test.txt")


if __name__ == "__main__":
    unittest.main()