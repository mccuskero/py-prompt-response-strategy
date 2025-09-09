"""Simple prompt creation strategy implementation."""

from typing import Dict, Any, Optional
from jinja2 import Template

from .interface import PromptCreationStrategy
from ..core.exceptions import ValidationError


class SimplePromptCreationStrategy(PromptCreationStrategy):
    """Simple implementation of prompt creation strategy."""
    
    def __init__(self):
        """Initialize the simple prompt strategy."""
        self.default_template = """
Please analyze the following information and provide a structured response:

{% if context %}
Context: {{ context | tojson }}
{% endif %}

Input Data:
{{ data | tojson }}

Please provide your response in a clear, structured format that can be easily parsed.
        """.strip()
    
    def create_prompt(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a structured prompt from input data.
        
        Args:
            data: Input data for prompt generation
            context: Optional context information
            
        Returns:
            Generated prompt string
            
        Raises:
            ValidationError: If data validation fails
        """
        if not self.validate_input(data):
            raise ValidationError("Input data validation failed")
        
        try:
            template = Template(self.default_template)
            return template.render(data=data, context=context)
        except Exception as e:
            raise ValidationError(f"Failed to render prompt template: {str(e)}")
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data against prompt requirements.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if data is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError("Input data must be a dictionary")
        
        if not data:
            raise ValidationError("Input data cannot be empty")
        
        return True
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": "SimplePromptCreationStrategy",
            "description": "Basic prompt creation using Jinja2 templates",
            "supports_context": True,
            "template_engine": "jinja2",
            "version": "1.0.0"
        }