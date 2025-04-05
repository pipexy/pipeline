"""
RESTAdapter.py - Adapter for RESTful API operations
"""

import requests
from .ChainableAdapter import ChainableAdapter

class RESTAdapter(ChainableAdapter):
    def __init__(self, name=None):
        # Initialize with empty params dictionary, not with the name
        super().__init__({})
        self._name = name  # Store name separately
        self._method = 'GET'
        self._url = None
        self._headers = {}
        self._data = None
        self._json = None
        self._response = None
        self._auth = None
        self._verify = True
        self._cookies = None
        self._allow_redirects = True

    def get(self, url, params=None):
        """Set up a GET request"""
        self._method = 'GET'
        self._url = url
        if params:
            self._params = params
        return self

    def post(self, url, data=None, json=None):
        """Set up a POST request"""
        self._method = 'POST'
        self._url = url
        self._data = data
        self._json = json
        return self

    def put(self, url, data=None, json=None):
        """Set up a PUT request"""
        self._method = 'PUT'
        self._url = url
        self._data = data
        self._json = json
        return self

    def delete(self, url):
        """Set up a DELETE request"""
        self._method = 'DELETE'
        self._url = url
        return self

    def headers(self, headers):
        """Set request headers"""
        self._headers = headers
        return self

    def auth(self, auth):
        """Set authentication"""
        self._auth = auth
        return self

    def cookies(self, cookies):
        """Set cookies"""
        self._cookies = cookies
        return self

    def verify(self, verify=True):
        """Set SSL verification"""
        self._verify = verify
        return self

    def _execute_self(self, input_data=None):
        """Execute the REST request"""
        try:
            # If input_data is provided and we don't have data/json, use it
            if input_data is not None:
                if self._method in ['POST', 'PUT', 'PATCH']:
                    if self._data is None and self._json is None:
                        if isinstance(input_data, dict):
                            self._json = input_data
                        else:
                            self._data = input_data

            # Prepare request parameters
            kwargs = {
                'headers': self._headers,
                'verify': self._verify,
                'allow_redirects': self._allow_redirects,
                'timeout': 30  # Default timeout
            }

            # Add optional parameters if provided
            if hasattr(self, '_params') and isinstance(self._params, dict) and self._params:
                kwargs['params'] = self._params
            if self._data is not None:
                kwargs['data'] = self._data
            if self._json is not None:
                kwargs['json'] = self._json
            if self._auth is not None:
                kwargs['auth'] = self._auth
            if self._cookies is not None:
                kwargs['cookies'] = self._cookies

            # Make the request
            self._response = requests.request(
                method=self._method,
                url=self._url,
                **kwargs
            )

            # Handle response
            self._response.raise_for_status()

            # Try to return JSON, fall back to text
            try:
                return self._response.json()
            except ValueError:
                return self._response.text

        except Exception as e:
            error_msg = f"REST request failed: {str(e)}"
            raise RuntimeError(error_msg)