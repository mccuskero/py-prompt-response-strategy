"""Tests for the PromptStrategy base class."""

import pytest
from unittest.mock import Mock

from prompt_xml_strategies.core.prompt_strategy import PromptStrategy
from prompt_xml_strategies.core.prompt_context import PromptContext


class TestPromptStrategy:
    """Test cases for PromptStrategy abstract base class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that PromptStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PromptStrategy("test")
    
    def test_concrete_implementation(self):
        """Test that concrete implementations work correctly."""
        
        class ConcreteStrategy(PromptStrategy):
            def generate_prompt(self, context: PromptContext) -> str:
                return f"Generated prompt for {self.name}"
            
            def validate_context(self, context: PromptContext) -> bool:
                return True
        
        strategy = ConcreteStrategy("test_strategy", "Test description")
        
        assert strategy.name == "test_strategy"
        assert strategy.description == "Test description"
        assert str(strategy) == "ConcreteStrategy(name='test_strategy')"
    
    def test_get_template_variables(self):
        """Test template variable extraction."""
        
        class ConcreteStrategy(PromptStrategy):
            def generate_prompt(self, context: PromptContext) -> str:
                return "test"
            
            def validate_context(self, context: PromptContext) -> bool:
                return True
        
        strategy = ConcreteStrategy("test")
        context = PromptContext(
            data={"key": "value"},
            metadata={"meta": "data"}
        )
        
        variables = strategy.get_template_variables(context)
        
        assert "data" in variables
        assert "strategy" in variables
        assert "response_format" in variables
        assert "meta" in variables
        assert variables["data"] == {"key": "value"}
        assert variables["strategy"] == "test"
    
    def test_default_field_methods(self):
        """Test default implementations of field methods."""
        
        class ConcreteStrategy(PromptStrategy):
            def generate_prompt(self, context: PromptContext) -> str:
                return "test"
            
            def validate_context(self, context: PromptContext) -> bool:
                return True
        
        strategy = ConcreteStrategy("test")
        
        assert strategy.get_required_fields() == []
        assert strategy.get_optional_fields() == []