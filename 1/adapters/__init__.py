"""
Adapters Package Initialization Module

This module initializes the adapters package by importing various language, protocol, and utility adapters
and creating a centralized dictionary of available adapters.
"""

# Import base adapter classes
from .ChainableAdapter import ChainableAdapter
from .BaseAdapter import BaseAdapter

# Import language adapters
from .BashAdapter import BashAdapter
from .PHPAdapter import PHPAdapter
from .PythonAdapter import PythonAdapter
from .NodeAdapter import NodeAdapter
from .JavaAdapter import JavaAdapter
from .JavaScriptAdapter import JavaScriptAdapter
from .RubyAdapter import RubyAdapter
from .GoAdapter import GoAdapter
from .CSharpAdapter import CSharpAdapter
from .KotlinAdapter import KotlinAdapter
from .HaskellAdapter import HaskellAdapter
from .ScalaAdapter import ScalaAdapter
from .R_Adapter import R_Adapter

# Import protocol/format adapters
from .HttpClientAdapter import HttpClientAdapter
from .HttpServerAdapter import HttpServerAdapter
from .RESTAdapter import RESTAdapter
from .JSONAdapter import JSONAdapter
from .HTMLAdapter import HTMLAdapter
from .MarkdownAdapter import MarkdownAdapter
from .DataFrameAdapter import DataFrameAdapter
from .ZplAdapter import ZplAdapter
from .XMLAdapter import XMLAdapter

# Import utility adapters
from .DatabaseAdapter import DatabaseAdapter
from .RegexAdapter import RegexAdapter
from .GraphQLAdapter import GraphQLAdapter
from .FileAdapter import FileAdapter
from .BrowserAdapter import BrowserAdapter

# Create adapter instances - passing name parameter as required
bash = BashAdapter('bash')
php = PHPAdapter('php')
python = PythonAdapter('python')
node = NodeAdapter('node')
java = JavaAdapter('java')
javascript = JavaScriptAdapter('javascript')
ruby = RubyAdapter('ruby')
go = GoAdapter('go')
csharp = CSharpAdapter('csharp')
kotlin = KotlinAdapter('kotlin')
haskell = HaskellAdapter('haskell')
scala = ScalaAdapter('scala')
r = R_Adapter('r')

# Protocol/format adapters
http_client = HttpClientAdapter('http_client')
http_server = HttpServerAdapter('http_server')
rest = RESTAdapter('rest')
json = JSONAdapter('json')
html = HTMLAdapter('html')
markdown = MarkdownAdapter('markdown')
dataframe = DataFrameAdapter('dataframe')
zpl = ZplAdapter('zpl')
xml = XMLAdapter('xml')

# Utility adapters
database = DatabaseAdapter('database')
regex = RegexAdapter('regex')
graphql = GraphQLAdapter('graphql')
file = FileAdapter('file')
browser = BrowserAdapter('browser')

# Dictionary of available adapters
ADAPTERS = {
    # Language adapters
    'bash': bash,
    'php': php,
    'python': python,
    'node': node,
    'java': java,
    'javascript': javascript,
    'ruby': ruby,
    'go': go,
    'csharp': csharp,
    'kotlin': kotlin,
    'haskell': haskell,
    'scala': scala,
    'r': r,

    # Protocol/format adapters
    'http_client': http_client,
    'http_server': http_server,
    'rest': rest,
    'json': json,
    'html': html,
    'markdown': markdown,
    'dataframe': dataframe,
    'zpl': zpl,
    'xml': xml,

    # Utility adapters
    'database': database,
    'regex': regex,
    'graphql': graphql,
    'file': file,
    'browser': browser
}

# Helper functions for pipeline usage
def pipeline(*adapters):
    """Execute a sequence of adapters as a pipeline"""
    if not adapters:
        return None

    result = adapters[0].execute()
    for adapter in adapters[1:]:
        result = adapter(result).execute()
    return result

class Pipeline:
    """Helper class for managing complex pipelines with named outputs"""
    def __init__(self):
        self.results = {}

    def add(self, name, adapter):
        """Add named adapter to pipeline"""
        self.results[name] = adapter.execute()
        return self

    def get(self, name):
        """Get named result"""
        return self.results.get(name)

    def pipe(self, name, adapter):
        """Pipe result from named adapter"""
        return adapter(self.results.get(name))