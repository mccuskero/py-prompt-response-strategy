"""Abstract base class for prompt creation strategies."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .prompt_context import PromptContext


class PromptStrategy(ABC):
    """Abstract base class defining the prompt creation interface."""
    
    def __init__(self, name: str, description: str = "") -> None:
        """Initialize the strategy.
        
        Args:
            name: The strategy name
            description: Optional description of the strategy
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def generate_prompt(self, context: PromptContext) -> str:
        """Generate a structured prompt from the given context.
        
        Args:
            context: The prompt context containing data and schemas
            
        Returns:
            The generated prompt string
            
        Raises:
            ValidationError: If context validation fails
            TemplateError: If prompt template rendering fails
        """
        pass
    
    @abstractmethod
    def validate_context(self, context: PromptContext) -> bool:
        """Validate that the context is suitable for this strategy.
        
        Args:
            context: The prompt context to validate
            
        Returns:
            True if context is valid for this strategy
            
        Raises:
            ValidationError: If context is invalid
        """
        pass
    
    def get_template_variables(self, context: PromptContext) -> Dict[str, Any]:
        """Extract template variables from context.
        
        Args:
            context: The prompt context
            
        Returns:
            Dictionary of template variables
        """
        variables = {
            "data": context.data,
            "strategy": self.name,
            "response_format": context.response_schema,
        }
        
        if context.metadata:
            variables.update(context.metadata)
            
        return variables
    
    def get_required_fields(self) -> list[str]:
        """Get list of required fields for this strategy.
        
        Returns:
            List of required field names
        """
        return []
    
    def get_optional_fields(self) -> list[str]:
        """Get list of optional fields for this strategy.
        
        Returns:
            List of optional field names
        """
        return []
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"