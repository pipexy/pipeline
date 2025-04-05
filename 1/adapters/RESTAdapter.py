"""
RESTAdapter.py
"""
import requests
import json
from .ChainableAdapter import ChainableAdapter


class RESTAdapter(ChainableAdapter):
    """Adapter for making REST API requests."""

    def __init__(self, params=None):
        super().__init__(params)
        self._method = "GET"
        self._url = None
        self._headers = {}
        self._response = None

    def get(self, url):
        """Set up GET request."""
        self._method = "GET"
        self._url = url
        return self

    def post(self, url):
        """Set up POST request."""
        self._method = "POST"
        self._url = url
        return self

    def put(self, url):
        """Set up PUT request."""
        self._method = "PUT"
        self._url = url
        return self

    def delete(self, url):
        """Set up DELETE request."""
        self._method = "DELETE"
        self._url = url
        return self

    def headers(self, headers):
        """Set request headers."""
        self._headers.update(headers)
        return self

    def auth(self, username, password):
        """Set basic authentication."""
        self._params['auth'] = (username, password)
        return self

    def bearer_token(self, token):
        """Set bearer token."""
        self._headers['Authorization'] = f"Bearer {token}"
        return self

    def timeout(self, seconds):
        """Set request timeout."""
        self._params['timeout'] = seconds
        return self

    def _execute_self(self, input_data=None):
        try:
            if not self._url:
                raise ValueError("URL must be specified for REST request")

            # Prepare request parameters
            kwargs = {
                'headers': self._headers,
                'timeout': self._params.get('timeout', 30)
            }

            # Add auth if specified
            if 'auth' in self._params:
                kwargs['auth'] = self._params['auth']

            # Handle data/json payload
            if input_data is not None:
                if isinstance(input_data, (dict, list)):
                    kwargs['json'] = input_data
                else:
                    kwargs['data'] = input_data
            elif 'data' in self._params:
                kwargs['data'] = self._params['data']
            elif 'json' in self._params:
                kwargs['json'] = self._params['json']

            # Make the request
            self._response = requests.request(
                method=self._method,
                url=self._url,
                **kwargs
            )

            # Check for success
            self._response.raise_for_status()

            # Try to return JSON if possible
            try:
                return self._response.json()
            except json.JSONDecodeError:
                return self._response.text

        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"REST request failed: {e} - Status code: {e.response.status_code}"
                try:
                    error_json = e.response.json()
                    error_msg += f" - Response: {error_json}"
                except:
                    error_msg += f" - Response: {e.response.text}"
            else:
                error_msg = f"REST request failed: {str(e)}"

            raise RuntimeError(error_msg)

    def reset(self):
        """Resets adapter state."""
        self._method = "GET"
        self._url = None
        self._headers = {}
        self._response = None
        self._params = {}
        return self