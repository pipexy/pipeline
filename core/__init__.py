# Inicjalizacja rdzenia
"""
Moduł inicjalizacyjny rdzenia systemu.
"""

from .pipeline_engine import PipelineEngine
from .workflow_engine import WorkflowEngine
from .dsl_parser import DotNotationParser, YamlDSLParser
from .adapter_manager import AdapterManager
from .context import ExecutionContext

# Wersja
__version__ = '1.0.0'