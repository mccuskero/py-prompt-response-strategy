"""Tests for the SchemaValidator class."""

import json
import pytest
from pathlib import Path

from prompt_xml_strategies.core.schema_validator import SchemaValidator, ValidationError


class TestSchemaValidator:
    """Test cases for SchemaValidator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator()
    
    def test_validate_simple_json_schema(self):
        """Test validation of a simple JSON schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        assert self.validator.validate_json_schema(schema) is True
    
    def test_validate_invalid_json_schema(self):
        """Test validation of invalid JSON schema."""
        invalid_schema = {
            "type": "invalid_type",
            "properties": "not_an_object"
        }
        
        with pytest.raises(ValidationError):
            self.validator.validate_json_schema(invalid_schema)
    
    def test_validate_data_against_schema_success(self):
        """Test successful data validation against schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        data = {"name": "John", "age": 30}
        
        assert self.validator.validate_data_against_schema(data, schema) is True
    
    def test_validate_data_against_schema_failure(self):
        """Test data validation failure against schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        # Missing required field
        data = {"age": 30}
        
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate_data_against_schema(data, schema)
        
        assert "validation failed" in str(exc_info.value).lower()
    
    def test_validate_prompt_context(self):
        """Test prompt context validation."""
        schema = {
            "type": "object",
            "properties": {
                "question": {"type": "string"}
            },
            "required": ["question"]
        }
        
        data = {"question": "What is the meaning of life?"}
        
        assert self.validator.validate_prompt_context(data, schema) is True
    
    def test_validate_response_data(self):
        """Test response data validation."""
        schema = {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["answer"]
        }
        
        response_data = {
            "answer": "42",
            "confidence": 0.95
        }
        
        assert self.validator.validate_response_data(response_data, schema) is True
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # First add something to cache
        schema = {"type": "object", "properties": {"test": {"type": "string"}}}
        data = {"test": "value"}
        
        self.validator.validate_data_against_schema(data, schema)
        
        # Check cache has items
        cache_count = self.validator.get_cached_schemas_count()
        assert cache_count["json_schemas"] > 0
        
        # Clear cache
        self.validator.clear_cache()
        
        # Check cache is empty
        cache_count = self.validator.get_cached_schemas_count()
        assert cache_count["json_schemas"] == 0
        assert cache_count["xsd_schemas"] == 0