# tests/test_graphql_adapter.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import json

# Import the adapter to test
sys.path.append('..')
from adapters.GraphQLAdapter import GraphQLAdapter


class GraphQLAdapterTest(unittest.TestCase):
    def setUp(self):
        # Setup test config
        self.config = {
            "endpoint": "https://api.example.com/graphql",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token"
            }
        }

        # Sample query
        self.test_query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                name
                email
                posts {
                    id
                    title
                }
            }
        }
        """

        # Sample variables
        self.test_variables = {
            "id": "1"
        }

        # Sample response
        self.sample_response = {
            "data": {
                "user": {
                    "id": "1",
                    "name": "Test User",
                    "email": "test@example.com",
                    "posts": [
                        {
                            "id": "101",
                            "title": "First Post"
                        },
                        {
                            "id": "102",
                            "title": "Second Post"
                        }
                    ]
                }
            }
        }

    def test_initialization(self):
        """Test basic initialization of GraphQLAdapter"""
        adapter = GraphQLAdapter(self.config)
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.config, self.config)

    @patch('requests.post')
    def test_query(self, mock_post):
        """Test executing a GraphQL query"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_response
        mock_post.return_value = mock_response

        adapter = GraphQLAdapter(self.config)
        adapter.query(self.test_query, self.test_variables)
        result = adapter.execute()

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            self.config["endpoint"],
            headers=self.config["headers"],
            json={
                "query": self.test_query,
                "variables": self.test_variables
            }
        )

        # Verify the response
        self.assertEqual(result, self.sample_response["data"])
        self.assertEqual(result["user"]["name"], "Test User")

    @patch('requests.post')
    def test_mutation(self, mock_post):
        """Test executing a GraphQL mutation"""
        # Sample mutation
        mutation = """
        mutation CreateUser($input: UserInput!) {
            createUser(input: $input) {
                id
                name
                email
            }
        }
        """

        # Variables for mutation
        variables = {
            "input": {
                "name": "New User",
                "email": "new@example.com"
            }
        }

        # Mock response for mutation
        mutation_response = {
            "data": {
                "createUser": {
                    "id": "2",
                    "name": "New User",
                    "email": "new@example.com"
                }
            }
        }

        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mutation_response
        mock_post.return_value = mock_response

        adapter = GraphQLAdapter(self.config)
        adapter.mutation(mutation, variables)
        result = adapter.execute()

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            self.config["endpoint"],
            headers=self.config["headers"],
            json={
                "query": mutation,
                "variables": variables
            }
        )

        # Verify the response
        self.assertEqual(result, mutation_response["data"])
        self.assertEqual(result["createUser"]["name"], "New User")

    @patch('requests.post')
    def test_error_handling(self, mock_post):
        """Test handling GraphQL errors"""
        # Mock a response with GraphQL errors
        error_response = {
            "errors": [
                {
                    "message": "User not found",
                    "locations": [{"line": 2, "column": 3}],
                    "path": ["user"]
                }
            ],
            "data": None
        }

        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200  # GraphQL errors have 200 status but errors in payload
        mock_response.json.return_value = error_response
        mock_post.return_value = mock_response

        adapter = GraphQLAdapter(self.config)
        adapter.query(self.test_query, self.test_variables)

        # Should raise an exception
        with self.assertRaises(Exception):
            adapter.execute()

    @patch('requests.post')
    def test_http_error_handling(self, mock_post):
        """Test handling HTTP errors"""
        # Mock an HTTP error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_post.return_value = mock_response

        adapter = GraphQLAdapter(self.config)
        adapter.query(self.test_query, self.test_variables)

        # Should raise an exception
        with self.assertRaises(Exception):
            adapter.execute()

    @patch('requests.post')
    def test_query_with_headers(self, mock_post):
        """Test query with additional custom headers"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_response
        mock_post.return_value = mock_response

        # Custom headers for this request
        custom_headers = {
            "X-Custom-Header": "test-value"
        }

        adapter = GraphQLAdapter(self.config)
        adapter.query(self.test_query, self.test_variables)
        adapter.headers(custom_headers)
        result = adapter.execute()

        # Verify the request was made with merged headers
        expected_headers = {**self.config["headers"], **custom_headers}
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args[1]["headers"], expected_headers)

        # Verify the response
        self.assertEqual(result["user"]["name"], "Test User")


if __name__ == "__main__":
    unittest.main()