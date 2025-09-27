"""
PromptXML Strategies Framework

A Python framework for creating structured prompts using JSON schemas 
with JSON-to-XML transformation capabilities.
"""

__version__ = "0.1.0"
__author__ = "PromptXML Team"
__email__ = "team@promptxml.dev"

from .core.pipeline import TripleStrategyPipeline
from .core.strategy_manager import StrategyManager, get_global_strategy_manager
from .core.exceptions import ValidationError, PipelineError, StrategyError

# Strategy interfaces
from .prompt_strategies.interface import PromptCreationStrategy
from .response_strategies.interface import ResponseCreationStrategy
from .xml_output_strategies.interface import XmlOutputStrategy

# Default implementations
from .prompt_strategies import SimplePromptCreationStrategy
from .response_strategies import SimpleResponseCreationStrategy
from .xml_output_strategies import SimpleXmlOutputStrategy

# LLM clients
from .llm_clients.base_client import BaseLLMClient, LLMError
from .llm_clients.openwebui_client import OpenWebUIClient
from .llm_clients.anthropic_client import AnthropicClient

__all__ = [
    # Core components
    "TripleStrategyPipeline",
    "StrategyManager",
    "get_global_strategy_manager",
    
    # Exceptions
    "ValidationError",
    "PipelineError", 
    "StrategyError",
    "LLMError",
    
    # Strategy interfaces
    "PromptCreationStrategy",
    "ResponseCreationStrategy",
    "XmlOutputStrategy",
    
    # Default implementations
    "SimplePromptCreationStrategy",
    "SimpleResponseCreationStrategy",
    "SimpleXmlOutputStrategy",
    
    # LLM clients
    "BaseLLMClient",
    "OpenWebUIClient",
    "AnthropicClient",
]