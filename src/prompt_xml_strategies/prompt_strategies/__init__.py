"""Prompt creation strategies package."""

from .interface import PromptCreationStrategy
from .simple_prompt_strategy import SimplePromptCreationStrategy

__all__ = ['PromptCreationStrategy', 'SimplePromptCreationStrategy']