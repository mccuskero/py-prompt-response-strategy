"""Schema validation for JSON schemas and XSD schemas."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jsonschema
import xmlschema
from lxml import etree
from pydantic import BaseModel


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, errors: Optional[List[str]] = None) -> None:
        """Initialize validation error.
        
        Args:
            message: The error message
            errors: List of detailed error messages
        """
        super().__init__(message)
        self.errors = errors or []


class SchemaValidator:
    """Validates JSON schemas (prompt/response) and XSD schemas."""
    
    def __init__(self) -> None:
        """Initialize the schema validator."""
        self._json_validators: Dict[str, jsonschema.Draft7Validator] = {}
        self._xsd_validators: Dict[str, xmlschema.XMLSchema] = {}
    
    def validate_json_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate a JSON schema itself.
        
        Args:
            schema: The JSON schema to validate
            
        Returns:
            True if schema is valid
            
        Raises:
            ValidationError: If schema is invalid
        """
        try:
            jsonschema.Draft7Validator.check_schema(schema)
            return True
        except jsonschema.SchemaError as e:
            raise ValidationError(f"Invalid JSON schema: {e.message}", [str(e)])
    
    def validate_data_against_schema(
        self, 
        data: Dict[str, Any], 
        schema: Dict[str, Any],
        schema_name: str = "data"
    ) -> bool:
        """Validate data against a JSON schema.
        
        Args:
            data: The data to validate
            schema: The JSON schema
            schema_name: Name of the schema for error reporting
            
        Returns:
            True if data is valid
            
        Raises:
            ValidationError: If data is invalid
        """
        try:
            # First validate the schema itself
            self.validate_json_schema(schema)
            
            # Create or get cached validator
            schema_key = json.dumps(schema, sort_keys=True)
            if schema_key not in self._json_validators:
                self._json_validators[schema_key] = jsonschema.Draft7Validator(schema)
            
            validator = self._json_validators[schema_key]
            
            # Validate the data
            errors = list(validator.iter_errors(data))
            if errors:
                error_messages = [f"{error.json_path}: {error.message}" for error in errors]
                raise ValidationError(
                    f"Data validation failed against {schema_name} schema",
                    error_messages
                )
            
            return True
            
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Validation error: {e.message}", [str(e)])
        except Exception as e:
            raise ValidationError(f"Unexpected error during validation: {str(e)}")
    
    def load_xsd_schema(self, xsd_path: Union[str, Path]) -> xmlschema.XMLSchema:
        """Load and cache an XSD schema.
        
        Args:
            xsd_path: Path to the XSD schema file
            
        Returns:
            The loaded XML schema
            
        Raises:
            ValidationError: If schema cannot be loaded
        """
        path = Path(xsd_path)
        path_str = str(path.absolute())
        
        if path_str not in self._xsd_validators:
            try:
                if not path.exists():
                    raise ValidationError(f"XSD schema file not found: {path}")
                
                self._xsd_validators[path_str] = xmlschema.XMLSchema(str(path))
            except Exception as e:
                raise ValidationError(f"Failed to load XSD schema from {path}: {str(e)}")
        
        return self._xsd_validators[path_str]
    
    def validate_xml_against_xsd(
        self, 
        xml_content: Union[str, bytes, etree.Element], 
        xsd_path: Union[str, Path]
    ) -> bool:
        """Validate XML content against an XSD schema.
        
        Args:
            xml_content: The XML content to validate
            xsd_path: Path to the XSD schema file
            
        Returns:
            True if XML is valid
            
        Raises:
            ValidationError: If XML is invalid
        """
        try:
            schema = self.load_xsd_schema(xsd_path)
            
            # Parse XML if it's a string or bytes
            if isinstance(xml_content, (str, bytes)):
                if isinstance(xml_content, str):
                    xml_content = xml_content.encode('utf-8')
                xml_doc = etree.fromstring(xml_content)
            else:
                xml_doc = xml_content
            
            # Validate using xmlschema
            schema.validate(xml_doc)
            return True
            
        except xmlschema.XMLSchemaException as e:
            raise ValidationError(f"XSD validation failed: {str(e)}")
        except etree.XMLSyntaxError as e:
            raise ValidationError(f"XML parsing error: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Unexpected error during XSD validation: {str(e)}")
    
    def validate_prompt_context(
        self, 
        data: Dict[str, Any], 
        prompt_schema: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Validate prompt context data.
        
        Args:
            data: The prompt data to validate
            prompt_schema: Optional prompt schema
            
        Returns:
            True if context is valid
            
        Raises:
            ValidationError: If context is invalid
        """
        if prompt_schema:
            return self.validate_data_against_schema(data, prompt_schema, "prompt")
        return True
    
    def validate_response_data(
        self, 
        response_data: Dict[str, Any], 
        response_schema: Dict[str, Any]
    ) -> bool:
        """Validate response data against response schema.
        
        Args:
            response_data: The response data to validate
            response_schema: The response schema
            
        Returns:
            True if response is valid
            
        Raises:
            ValidationError: If response is invalid
        """
        return self.validate_data_against_schema(
            response_data, 
            response_schema, 
            "response"
        )
    
    def clear_cache(self) -> None:
        """Clear all cached validators."""
        self._json_validators.clear()
        self._xsd_validators.clear()
    
    def get_cached_schemas_count(self) -> Dict[str, int]:
        """Get count of cached schemas.
        
        Returns:
            Dictionary with counts of cached schemas
        """
        return {
            "json_schemas": len(self._json_validators),
            "xsd_schemas": len(self._xsd_validators),
        }