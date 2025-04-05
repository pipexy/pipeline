#!/usr/bin/env python3
# adapters.py
import subprocess
import os
import json
import tempfile
from typing import Dict, Any, List, Union

# Import adapters from the adapters package
from adapters.BashAdapter import BashAdapter
from adapters.PHPAdapter import PHPAdapter
from adapters.NodeAdapter import NodeAdapter
from adapters.HttpClientAdapter import HttpClientAdapter
from adapters.HttpServerAdapter import HttpServerAdapter
from adapters.PythonAdapter import PythonAdapter
from adapters.JavaAdapter import JavaAdapter
from adapters.JavaScriptAdapter import JavaScriptAdapter
from adapters.JavaAdapter import JavaAdapter
from adapters.RubyAdapter import RubyAdapter
from adapters.GoAdapter import GoAdapter
from adapters.CSharpAdapter import CSharp

bash = BashAdapter('bash')
php = PHPAdapter('php')
node = NodeAdapter('node')
http_client = HttpClientAdapter('http_client')
http_server = HttpServerAdapter('http_server')
python = PythonAdapter('python')

# Słownik dostępnych adapterów
ADAPTERS = {
    'bash': bash,
    'php': php,
    'node': node,
    'http_client': http_client,
    'http_server': http_server,
    'python': python
}


