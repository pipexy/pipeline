# This file makes the adapters directory a Python package
# Import adapter classes
from .BaseAdapter import BaseAdapter
from .BashAdapter import BashAdapter
from .PHPAdapter import PHPAdapter
from .NodeAdapter import NodeAdapter
from .HttpClientAdapter import HttpClientAdapter
from .HttpServerAdapter import HttpServerAdapter
from .PythonAdapter import PythonAdapter
from .JavaAdapter import JavaAdapter
from .JavaScriptAdapter import JavaScriptAdapter
from .JavaAdapter import JavaAdapter
from .RubyAdapter import RubyAdapter
from .GoAdapter import GoAdapter
from .CSharpAdapter import CSharpAdapter

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
