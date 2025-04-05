"""
GraphQLAdapter.py
"""
import requests
import json
from .ChainableAdapter import ChainableAdapter


class GraphQLAdapter(ChainableAdapter):
    """Adapter for making GraphQL queries."""

    def __init__(self, params=None):
        super().__init__(params)
        self._endpoint = None
        self._query = None
        self._variables = {}
        self._headers = {'Content-Type': 'application/json'}
        self._operation_name = None

    def endpoint(self, url):
        """Set GraphQL endpoint URL."""
        self._endpoint = url
        return self

    def query(self, query_string):
        """Set GraphQL query or mutation."""
        self._query = query_string
        return self

    def variables(self, variables_dict):
        """Set variables for the query."""
        self._variables.update(variables_dict)
        return self

    def operation(self, operation_name):
        """Set operation name for the query."""
        self._operation_name = operation_name
        return self

    def headers(self, headers_dict):
        """Set HTTP headers for the request."""
        self._headers.update(headers_dict)
        return self

    def auth_token(self, token):
        """Set authentication token."""
        self._headers['Authorization'] = f"Bearer {token}"
        return self

    def _execute_self(self, input_data=None):
        try:
            if not self._endpoint:
                raise ValueError("GraphQL endpoint URL must be specified")

            if not self._query:
                if isinstance(input_data, str):
                    self._query = input_data
                else:
                    raise ValueError("GraphQL query must be provided")

            # Prepare request payload
            payload = {
                'query': self._query,
                'variables': self._variables
            }

            if self._operation_name:
                payload['operationName'] = self._operation_name

            # Make the request
            response = requests.post(
                self._endpoint,
                headers=self._headers,
                json=payload
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Check for GraphQL errors
            if 'errors' in result:
                errors = result['errors']
                error_messages = [e.get('message', 'Unknown GraphQL error') for e in errors]
                raise RuntimeError(f"GraphQL errors: {'; '.join(error_messages)}")

            # Return data
            if 'data' in result:
                return result['data']
            return result

        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"GraphQL request failed: {e} - Status code: {e.response.status_code}"
                try:
                    error_json = e.response.json()
                    error_msg += f" - Response: {error_json}"
                except:
                    error_msg += f" - Response: {e.response.text}"
            else:
                error_msg = f"GraphQL request failed: {str(e)}"

            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"GraphQL operation failed: {str(e)}")

    def reset(self):
        """Reset adapter state."""
        self._endpoint = None
        self._query = None
        self._variables = {}
        self._headers = {'Content-Type': 'application/json'}
        self._operation_name = None
        self._params = {}
        return self