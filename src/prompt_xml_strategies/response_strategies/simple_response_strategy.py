"""Simple response creation strategy implementation."""

import json
import re
from typing import Dict, Any, Optional

from .interface import ResponseCreationStrategy
from ..core.exceptions import ValidationError


class SimpleResponseCreationStrategy(ResponseCreationStrategy):
    """Simple implementation of response creation strategy."""
    
    def __init__(self):
        """Initialize the simple response strategy."""
        self.json_pattern = re.compile(r'```json\s*\n(.*?)\n```', re.DOTALL)
    
    def process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process raw LLM response into structured data.
        
        Args:
            raw_response: Raw response from LLM
            context: Optional context information
            
        Returns:
            Structured response data
            
        Raises:
            ValidationError: If response processing fails
        """
        if not raw_response or not raw_response.strip():
            raise ValidationError("Response cannot be empty")
        
        # Try to extract JSON from code blocks first
        json_match = self.json_pattern.search(raw_response)
        if json_match:
            json_str = json_match.group(1)
            try:
                parsed_data = json.loads(json_str)
                if self.validate_response(parsed_data):
                    return parsed_data
            except json.JSONDecodeError as e:
                raise ValidationError(f"Failed to parse JSON from response: {str(e)}")
        
        # Try to parse the entire response as JSON
        try:
            parsed_data = json.loads(raw_response)
            if self.validate_response(parsed_data):
                return parsed_data
        except json.JSONDecodeError:
            # If JSON parsing fails, create a structured response
            return self._create_fallback_response(raw_response, context)
    
    def _create_fallback_response(
        self, 
        raw_response: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a fallback structured response when JSON parsing fails.
        
        Args:
            raw_response: Raw response text
            context: Optional context information
            
        Returns:
            Structured response dictionary
        """
        return {
            "content": raw_response.strip(),
            "type": "text",
            "processed": True,
            "metadata": {
                "fallback_used": True,
                "original_length": len(raw_response),
                "context": context or {}
            }
        }
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate processed response against schema.
        
        Args:
            response: Processed response data
            
        Returns:
            True if response is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(response, dict):
            raise ValidationError("Response must be a dictionary")
        
        # Basic validation - response should have some content
        if not response:
            raise ValidationError("Response cannot be empty")
        
        return True
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": "SimpleResponseCreationStrategy",
            "description": "Basic response processing with JSON extraction and fallback",
            "supports_json": True,
            "supports_fallback": True,
            "version": "1.0.0"
        }