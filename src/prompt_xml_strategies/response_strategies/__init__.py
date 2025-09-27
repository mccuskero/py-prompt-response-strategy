"""Response creation strategies package."""

from .interface import ResponseCreationStrategy
from .simple_response_strategy import SimpleResponseCreationStrategy

__all__ = ['ResponseCreationStrategy', 'SimpleResponseCreationStrategy']