"""Tests for the strategy manager."""

import pytest

from prompt_xml_strategies.core.strategy_manager import StrategyManager, get_global_strategy_manager
from prompt_xml_strategies.core.exceptions import StrategyError
from prompt_xml_strategies.prompt_strategies import SimplePromptCreationStrategy
from prompt_xml_strategies.response_strategies import SimpleResponseCreationStrategy
from prompt_xml_strategies.xml_output_strategies import SimpleXmlOutputStrategy


class TestStrategyManager:
    """Test cases for StrategyManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = StrategyManager()
    
    def test_register_and_get_prompt_strategy(self):
        """Test registering and getting a prompt strategy."""
        self.manager.register_prompt_strategy(SimplePromptCreationStrategy, "test")
        
        strategy = self.manager.get_prompt_strategy("test")
        assert isinstance(strategy, SimplePromptCreationStrategy)
    
    def test_register_duplicate_prompt_strategy(self):
        """Test registering duplicate prompt strategy."""
        self.manager.register_prompt_strategy(SimplePromptCreationStrategy, "test")
        
        with pytest.raises(StrategyError, match="Prompt strategy 'test' already registered"):
            self.manager.register_prompt_strategy(SimplePromptCreationStrategy, "test")
    
    def test_get_nonexistent_prompt_strategy(self):
        """Test getting non-existent prompt strategy."""
        with pytest.raises(StrategyError, match="Prompt strategy 'nonexistent' not registered"):
            self.manager.get_prompt_strategy("nonexistent")
    
    def test_list_prompt_strategies(self):
        """Test listing prompt strategies."""
        assert self.manager.list_prompt_strategies() == []
        
        self.manager.register_prompt_strategy(SimplePromptCreationStrategy, "test1")
        self.manager.register_prompt_strategy(SimplePromptCreationStrategy, "test2")
        
        strategies = self.manager.list_prompt_strategies()
        assert "test1" in strategies
        assert "test2" in strategies
        assert len(strategies) == 2
    
    def test_register_and_get_response_strategy(self):
        """Test registering and getting a response strategy."""
        self.manager.register_response_strategy(SimpleResponseCreationStrategy, "test")
        
        strategy = self.manager.get_response_strategy("test")
        assert isinstance(strategy, SimpleResponseCreationStrategy)
    
    def test_register_duplicate_response_strategy(self):
        """Test registering duplicate response strategy."""
        self.manager.register_response_strategy(SimpleResponseCreationStrategy, "test")
        
        with pytest.raises(StrategyError, match="Response strategy 'test' already registered"):
            self.manager.register_response_strategy(SimpleResponseCreationStrategy, "test")
    
    def test_get_nonexistent_response_strategy(self):
        """Test getting non-existent response strategy."""
        with pytest.raises(StrategyError, match="Response strategy 'nonexistent' not registered"):
            self.manager.get_response_strategy("nonexistent")
    
    def test_list_response_strategies(self):
        """Test listing response strategies."""
        assert self.manager.list_response_strategies() == []
        
        self.manager.register_response_strategy(SimpleResponseCreationStrategy, "test1")
        self.manager.register_response_strategy(SimpleResponseCreationStrategy, "test2")
        
        strategies = self.manager.list_response_strategies()
        assert "test1" in strategies
        assert "test2" in strategies
        assert len(strategies) == 2
    
    def test_register_and_get_xml_strategy(self):
        """Test registering and getting an XML strategy."""
        self.manager.register_xml_strategy(SimpleXmlOutputStrategy, "test")
        
        strategy = self.manager.get_xml_strategy("test")
        assert isinstance(strategy, SimpleXmlOutputStrategy)
    
    def test_register_duplicate_xml_strategy(self):
        """Test registering duplicate XML strategy."""
        self.manager.register_xml_strategy(SimpleXmlOutputStrategy, "test")
        
        with pytest.raises(StrategyError, match="XML strategy 'test' already registered"):
            self.manager.register_xml_strategy(SimpleXmlOutputStrategy, "test")
    
    def test_get_nonexistent_xml_strategy(self):
        """Test getting non-existent XML strategy."""
        with pytest.raises(StrategyError, match="XML strategy 'nonexistent' not registered"):
            self.manager.get_xml_strategy("nonexistent")
    
    def test_list_xml_strategies(self):
        """Test listing XML strategies."""
        assert self.manager.list_xml_strategies() == []
        
        self.manager.register_xml_strategy(SimpleXmlOutputStrategy, "test1")
        self.manager.register_xml_strategy(SimpleXmlOutputStrategy, "test2")
        
        strategies = self.manager.list_xml_strategies()
        assert "test1" in strategies
        assert "test2" in strategies
        assert len(strategies) == 2
    
    def test_register_default_strategies(self):
        """Test registering default strategies."""
        self.manager.register_default_strategies()
        
        assert "simple" in self.manager.list_prompt_strategies()
        assert "simple" in self.manager.list_response_strategies()
        assert "simple" in self.manager.list_xml_strategies()
    
    def test_get_all_strategies_info(self):
        """Test getting all strategies info."""
        self.manager.register_default_strategies()
        
        info = self.manager.get_all_strategies_info()
        
        assert "prompt_strategies" in info
        assert "response_strategies" in info
        assert "xml_strategies" in info
        
        assert "simple" in info["prompt_strategies"]
        assert "simple" in info["response_strategies"]
        assert "simple" in info["xml_strategies"]
    
    def test_clear_all(self):
        """Test clearing all strategies."""
        self.manager.register_default_strategies()
        
        assert len(self.manager.list_prompt_strategies()) > 0
        assert len(self.manager.list_response_strategies()) > 0
        assert len(self.manager.list_xml_strategies()) > 0
        
        self.manager.clear_all()
        
        assert len(self.manager.list_prompt_strategies()) == 0
        assert len(self.manager.list_response_strategies()) == 0
        assert len(self.manager.list_xml_strategies()) == 0


def test_get_global_strategy_manager():
    """Test getting global strategy manager."""
    manager1 = get_global_strategy_manager()
    manager2 = get_global_strategy_manager()
    
    # Should return the same instance
    assert manager1 is manager2
    
    # Should have default strategies registered
    assert "simple" in manager1.list_prompt_strategies()
    assert "simple" in manager1.list_response_strategies()
    assert "simple" in manager1.list_xml_strategies()