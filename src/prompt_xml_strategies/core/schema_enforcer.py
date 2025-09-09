"""Ensures prompts include proper response format instructions."""

from typing import Dict, Any, Optional
from .response_schema_builder import ResponseSchemaBuilder


class SchemaEnforcer:
    """Ensures prompts include proper response format instructions."""
    
    def __init__(self) -> None:
        """Initialize the schema enforcer."""
        self.schema_builder = ResponseSchemaBuilder()
    
    def enforce_response_schema(
        self, 
        prompt: str, 
        response_schema: Dict[str, Any],
        instruction_style: str = "detailed"
    ) -> str:
        """Ensure prompt includes response format instructions.
        
        Args:
            prompt: The original prompt
            response_schema: The response schema
            instruction_style: Style of instructions to add
            
        Returns:
            Prompt with response format instructions
        """
        format_instructions = self.schema_builder.build_format_instructions(
            response_schema, 
            instruction_style
        )
        
        # Add format instructions to the prompt
        return f"{prompt}\n\n{format_instructions}"
    
    def validate_prompt_completeness(
        self, 
        prompt: str, 
        response_schema: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Validate that prompt includes necessary format instructions.
        
        Args:
            prompt: The prompt to validate
            response_schema: Optional response schema
            
        Returns:
            True if prompt appears complete
        """
        if response_schema:
            # Check if prompt mentions JSON format or response structure
            format_indicators = ["json", "format", "response", "structure"]
            return any(indicator in prompt.lower() for indicator in format_indicators)
        
        return True