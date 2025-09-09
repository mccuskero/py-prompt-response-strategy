"""Parse and validate LLM responses against expected schemas."""

import json
import re
from typing import Any, Dict, Optional

from .schema_validator import SchemaValidator, ValidationError


class ResponseParsingError(Exception):
    """Exception raised during response parsing."""
    pass


class ResponseParser:
    """Parses and validates LLM responses against expected response schemas."""
    
    def __init__(self, validator: Optional[SchemaValidator] = None) -> None:
        """Initialize the response parser.
        
        Args:
            validator: Optional schema validator instance
        """
        self.validator = validator or SchemaValidator()
    
    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from LLM response text.
        
        Args:
            response_text: The raw response text from LLM
            
        Returns:
            Parsed JSON data
            
        Raises:
            ResponseParsingError: If JSON parsing fails
        """
        # Try to extract JSON from response text
        json_text = self._extract_json_from_text(response_text)
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ResponseParsingError(f"Failed to parse JSON from response: {str(e)}")
    
    def parse_and_validate_response(
        self, 
        response_text: str, 
        response_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse and validate LLM response against schema.
        
        Args:
            response_text: The raw response text from LLM
            response_schema: The expected response schema
            
        Returns:
            Validated response data
            
        Raises:
            ResponseParsingError: If parsing fails
            ValidationError: If validation fails
        """
        # Parse JSON from response
        response_data = self.parse_json_response(response_text)
        
        # Validate against schema
        self.validator.validate_response_data(response_data, response_schema)
        
        return response_data
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON content from text that may contain other content.
        
        Args:
            text: The text containing JSON
            
        Returns:
            Extracted JSON string
            
        Raises:
            ResponseParsingError: If no valid JSON is found
        """
        # Clean the text
        text = text.strip()
        
        # Try to find JSON within code blocks (```json ... ```)
        json_code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_code_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try to find standalone JSON objects
        # Look for content that starts with { and ends with }
        brace_pattern = r'\{.*\}'
        match = re.search(brace_pattern, text, re.DOTALL)
        if match:
            # Validate that this looks like valid JSON by checking structure
            json_candidate = match.group(0)
            if self._looks_like_json(json_candidate):
                return json_candidate
        
        # If no JSON pattern found, try to parse the entire text
        if self._looks_like_json(text):
            return text
        
        raise ResponseParsingError(
            f"No valid JSON found in response text. Text: {text[:200]}..."
        )
    
    def _looks_like_json(self, text: str) -> bool:
        """Check if text looks like JSON.
        
        Args:
            text: The text to check
            
        Returns:
            True if text looks like JSON
        """
        text = text.strip()
        
        # Basic structural checks
        if not text:
            return False
        
        # Should start and end with braces for objects
        if text.startswith('{') and text.endswith('}'):
            try:
                # Try to parse to verify it's valid JSON
                json.loads(text)
                return True
            except json.JSONDecodeError:
                return False
        
        # Should start and end with brackets for arrays
        if text.startswith('[') and text.endswith(']'):
            try:
                json.loads(text)
                return True
            except json.JSONDecodeError:
                return False
        
        return False
    
    def extract_structured_data(
        self, 
        response_text: str, 
        expected_fields: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Extract structured data from response even if not in JSON format.
        
        Args:
            response_text: The response text
            expected_fields: Optional list of expected field names
            
        Returns:
            Dictionary with extracted data
        """
        # First try JSON extraction
        try:
            return self.parse_json_response(response_text)
        except ResponseParsingError:
            pass
        
        # Fallback to pattern-based extraction
        data = {}
        
        if expected_fields:
            for field in expected_fields:
                value = self._extract_field_value(response_text, field)
                if value is not None:
                    data[field] = value
        
        return data
    
    def _extract_field_value(self, text: str, field_name: str) -> Optional[str]:
        """Extract a field value from text using patterns.
        
        Args:
            text: The text to search
            field_name: The field name to find
            
        Returns:
            The extracted value or None
        """
        # Try various patterns to extract field values
        patterns = [
            rf'{field_name}:\s*"([^"]*)"',  # field: "value"
            rf'{field_name}:\s*([^\n\r,}}]+)',  # field: value
            rf'{field_name}\s*=\s*"([^"]*)"',  # field = "value"
            rf'{field_name}\s*=\s*([^\n\r,}}]+)',  # field = value
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def validate_response_completeness(
        self, 
        response_data: Dict[str, Any], 
        required_fields: list[str]
    ) -> bool:
        """Validate that response contains all required fields.
        
        Args:
            response_data: The parsed response data
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present
            
        Raises:
            ValidationError: If required fields are missing
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in response_data or response_data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(
                f"Response missing required fields: {missing_fields}",
                [f"Missing field: {field}" for field in missing_fields]
            )
        
        return True