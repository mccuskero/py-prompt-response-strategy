"""Tests for the simple strategy implementations."""

import pytest
import json
from xml.etree.ElementTree import Element

from prompt_xml_strategies.prompt_strategies import SimplePromptCreationStrategy
from prompt_xml_strategies.response_strategies import SimpleResponseCreationStrategy
from prompt_xml_strategies.xml_output_strategies import SimpleXmlOutputStrategy
from prompt_xml_strategies.core.exceptions import ValidationError


class TestSimplePromptCreationStrategy:
    """Test cases for SimplePromptCreationStrategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = SimplePromptCreationStrategy()
    
    def test_create_prompt_basic(self):
        """Test basic prompt creation."""
        data = {"task": "test", "content": "hello"}
        prompt = self.strategy.create_prompt(data)
        
        assert "test" in prompt
        assert "hello" in prompt
        assert "Input Data:" in prompt
    
    def test_create_prompt_with_context(self):
        """Test prompt creation with context."""
        data = {"task": "test"}
        context = {"user": "john"}
        
        prompt = self.strategy.create_prompt(data, context)
        
        assert "Context:" in prompt
        assert "john" in prompt
    
    def test_validate_input_success(self):
        """Test successful input validation."""
        data = {"key": "value"}
        assert self.strategy.validate_input(data) is True
    
    def test_validate_input_empty_dict(self):
        """Test validation with empty dictionary."""
        with pytest.raises(ValidationError, match="Input data cannot be empty"):
            self.strategy.validate_input({})
    
    def test_validate_input_non_dict(self):
        """Test validation with non-dictionary input."""
        with pytest.raises(ValidationError, match="Input data must be a dictionary"):
            self.strategy.validate_input("not a dict")
    
    def test_get_strategy_info(self):
        """Test getting strategy information."""
        info = self.strategy.get_strategy_info()
        
        assert info["name"] == "SimplePromptCreationStrategy"
        assert "jinja2" in info["template_engine"]
        assert info["supports_context"] is True


class TestSimpleResponseCreationStrategy:
    """Test cases for SimpleResponseCreationStrategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = SimpleResponseCreationStrategy()
    
    def test_process_response_json_in_code_block(self):
        """Test processing response with JSON in code blocks."""
        raw_response = """Here is the response:
```json
{"result": "success", "value": 42}
```
That's the data."""
        
        result = self.strategy.process_response(raw_response)
        
        assert result["result"] == "success"
        assert result["value"] == 42
    
    def test_process_response_pure_json(self):
        """Test processing pure JSON response."""
        raw_response = '{"status": "ok", "data": ["a", "b", "c"]}'
        
        result = self.strategy.process_response(raw_response)
        
        assert result["status"] == "ok"
        assert result["data"] == ["a", "b", "c"]
    
    def test_process_response_fallback(self):
        """Test fallback response processing."""
        raw_response = "This is just plain text response"
        
        result = self.strategy.process_response(raw_response)
        
        assert result["content"] == raw_response
        assert result["type"] == "text"
        assert result["metadata"]["fallback_used"] is True
    
    def test_process_response_empty(self):
        """Test processing empty response."""
        with pytest.raises(ValidationError, match="Response cannot be empty"):
            self.strategy.process_response("")
    
    def test_validate_response_success(self):
        """Test successful response validation."""
        response = {"key": "value"}
        assert self.strategy.validate_response(response) is True
    
    def test_validate_response_empty(self):
        """Test validation with empty response."""
        with pytest.raises(ValidationError, match="Response cannot be empty"):
            self.strategy.validate_response({})
    
    def test_validate_response_non_dict(self):
        """Test validation with non-dictionary response."""
        with pytest.raises(ValidationError, match="Response must be a dictionary"):
            self.strategy.validate_response("not a dict")
    
    def test_get_strategy_info(self):
        """Test getting strategy information."""
        info = self.strategy.get_strategy_info()
        
        assert info["name"] == "SimpleResponseCreationStrategy"
        assert info["supports_json"] is True
        assert info["supports_fallback"] is True


class TestSimpleXmlOutputStrategy:
    """Test cases for SimpleXmlOutputStrategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = SimpleXmlOutputStrategy()
    
    def test_transform_to_xml_basic(self):
        """Test basic XML transformation."""
        data = {"name": "test", "value": 42}
        
        xml_element = self.strategy.transform_to_xml(data)
        
        assert xml_element.tag == "response"
        assert xml_element.attrib["timestamp"]
        
        # Check child elements
        children = {child.tag: child.text for child in xml_element}
        assert children["name"] == "test"
        assert children["value"] == "42"
    
    def test_transform_to_xml_nested(self):
        """Test XML transformation with nested data."""
        data = {
            "user": {"name": "john", "age": 30},
            "settings": {"theme": "dark"}
        }
        
        xml_element = self.strategy.transform_to_xml(data)
        
        # Find nested elements
        user_elem = xml_element.find("user")
        assert user_elem is not None
        assert user_elem.find("name").text == "john"
        assert user_elem.find("age").text == "30"
    
    def test_transform_to_xml_with_arrays(self):
        """Test XML transformation with arrays."""
        data = {"items": ["apple", "banana", "cherry"]}
        
        xml_element = self.strategy.transform_to_xml(data)
        
        # Check array elements
        items = xml_element.findall("items")
        assert len(items) == 3
        assert items[0].text == "apple"
        assert items[1].text == "banana"
        assert items[2].text == "cherry"
        
        # Check index attributes
        for i, item in enumerate(items):
            assert item.get("index") == str(i)
    
    def test_transform_to_xml_with_context(self):
        """Test XML transformation with context."""
        data = {"message": "hello"}
        context = {"user_id": "123", "session": "abc"}
        
        xml_element = self.strategy.transform_to_xml(data, context)
        
        # Check context attributes
        assert xml_element.get("context_user_id") == "123"
        assert xml_element.get("context_session") == "abc"
    
    def test_clean_element_name(self):
        """Test element name cleaning."""
        # Test with invalid characters
        cleaned = self.strategy._clean_element_name("test-name with spaces!")
        assert cleaned == "test_name_with_spaces_"
        
        # Test with number at start
        cleaned = self.strategy._clean_element_name("123abc")
        assert cleaned == "_123abc"
        
        # Test empty name
        cleaned = self.strategy._clean_element_name("")
        assert cleaned == "element"
    
    def test_validate_xml_success(self):
        """Test successful XML validation."""
        element = Element("test")
        assert self.strategy.validate_xml(element) is True
    
    def test_validate_xml_none(self):
        """Test XML validation with None."""
        with pytest.raises(ValidationError, match="XML element cannot be None"):
            self.strategy.validate_xml(None)
    
    def test_transform_non_dict(self):
        """Test transformation with non-dictionary input."""
        with pytest.raises(ValidationError, match="Response data must be a dictionary"):
            self.strategy.transform_to_xml("not a dict")
    
    def test_get_strategy_info(self):
        """Test getting strategy information."""
        info = self.strategy.get_strategy_info()
        
        assert info["name"] == "SimpleXmlOutputStrategy"
        assert info["supports_nested_data"] is True
        assert info["supports_arrays"] is True
        assert info["root_element"] == "response"