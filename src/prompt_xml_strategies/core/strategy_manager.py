"""Strategy manager for handling all three strategy types."""

from typing import Dict, List, Type, Optional, Any

from ..prompt_strategies.interface import PromptCreationStrategy
from ..response_strategies.interface import ResponseCreationStrategy
from ..xml_output_strategies.interface import XmlOutputStrategy
from .exceptions import StrategyError


class StrategyManager:
    """Manager for all three types of strategies."""
    
    def __init__(self) -> None:
        """Initialize the strategy manager."""
        self._prompt_strategies: Dict[str, Type[PromptCreationStrategy]] = {}
        self._response_strategies: Dict[str, Type[ResponseCreationStrategy]] = {}
        self._xml_strategies: Dict[str, Type[XmlOutputStrategy]] = {}
        
        self._prompt_instances: Dict[str, PromptCreationStrategy] = {}
        self._response_instances: Dict[str, ResponseCreationStrategy] = {}
        self._xml_instances: Dict[str, XmlOutputStrategy] = {}
    
    # Prompt strategy methods
    def register_prompt_strategy(
        self, 
        strategy_class: Type[PromptCreationStrategy], 
        name: str
    ) -> None:
        """Register a prompt creation strategy.
        
        Args:
            strategy_class: The strategy class
            name: Strategy name
            
        Raises:
            StrategyError: If strategy is already registered
        """
        if name in self._prompt_strategies:
            raise StrategyError(f"Prompt strategy '{name}' already registered")
        
        self._prompt_strategies[name] = strategy_class
    
    def get_prompt_strategy(self, name: str) -> PromptCreationStrategy:
        """Get a prompt creation strategy instance.
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyError: If strategy not found
        """
        if name not in self._prompt_strategies:
            raise StrategyError(f"Prompt strategy '{name}' not registered")
        
        if name not in self._prompt_instances:
            strategy_class = self._prompt_strategies[name]
            self._prompt_instances[name] = strategy_class()
        
        return self._prompt_instances[name]
    
    def list_prompt_strategies(self) -> List[str]:
        """List all registered prompt strategies."""
        return list(self._prompt_strategies.keys())
    
    # Response strategy methods
    def register_response_strategy(
        self, 
        strategy_class: Type[ResponseCreationStrategy], 
        name: str
    ) -> None:
        """Register a response creation strategy.
        
        Args:
            strategy_class: The strategy class
            name: Strategy name
            
        Raises:
            StrategyError: If strategy is already registered
        """
        if name in self._response_strategies:
            raise StrategyError(f"Response strategy '{name}' already registered")
        
        self._response_strategies[name] = strategy_class
    
    def get_response_strategy(self, name: str) -> ResponseCreationStrategy:
        """Get a response creation strategy instance.
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyError: If strategy not found
        """
        if name not in self._response_strategies:
            raise StrategyError(f"Response strategy '{name}' not registered")
        
        if name not in self._response_instances:
            strategy_class = self._response_strategies[name]
            self._response_instances[name] = strategy_class()
        
        return self._response_instances[name]
    
    def list_response_strategies(self) -> List[str]:
        """List all registered response strategies."""
        return list(self._response_strategies.keys())
    
    # XML strategy methods
    def register_xml_strategy(
        self, 
        strategy_class: Type[XmlOutputStrategy], 
        name: str
    ) -> None:
        """Register an XML output strategy.
        
        Args:
            strategy_class: The strategy class
            name: Strategy name
            
        Raises:
            StrategyError: If strategy is already registered
        """
        if name in self._xml_strategies:
            raise StrategyError(f"XML strategy '{name}' already registered")
        
        self._xml_strategies[name] = strategy_class
    
    def get_xml_strategy(self, name: str) -> XmlOutputStrategy:
        """Get an XML output strategy instance.
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyError: If strategy not found
        """
        if name not in self._xml_strategies:
            raise StrategyError(f"XML strategy '{name}' not registered")
        
        if name not in self._xml_instances:
            strategy_class = self._xml_strategies[name]
            self._xml_instances[name] = strategy_class()
        
        return self._xml_instances[name]
    
    def list_xml_strategies(self) -> List[str]:
        """List all registered XML strategies."""
        return list(self._xml_strategies.keys())
    
    # General methods
    def get_all_strategies_info(self) -> Dict[str, Any]:
        """Get information about all registered strategies.
        
        Returns:
            Dictionary with strategy information
        """
        return {
            "prompt_strategies": {
                name: self.get_prompt_strategy(name).get_strategy_info()
                for name in self.list_prompt_strategies()
            },
            "response_strategies": {
                name: self.get_response_strategy(name).get_strategy_info()
                for name in self.list_response_strategies()
            },
            "xml_strategies": {
                name: self.get_xml_strategy(name).get_strategy_info()
                for name in self.list_xml_strategies()
            }
        }
    
    def register_default_strategies(self) -> None:
        """Register the default simple strategies."""
        from ..prompt_strategies import SimplePromptCreationStrategy
        from ..response_strategies import SimpleResponseCreationStrategy
        from ..xml_output_strategies import SimpleXmlOutputStrategy
        
        self.register_prompt_strategy(SimplePromptCreationStrategy, "simple")
        self.register_response_strategy(SimpleResponseCreationStrategy, "simple")
        self.register_xml_strategy(SimpleXmlOutputStrategy, "simple")
    
    def clear_all(self) -> None:
        """Clear all registered strategies."""
        self._prompt_strategies.clear()
        self._response_strategies.clear()
        self._xml_strategies.clear()
        self._prompt_instances.clear()
        self._response_instances.clear()
        self._xml_instances.clear()


# Global strategy manager instance
_global_manager: Optional[StrategyManager] = None


def get_global_strategy_manager() -> StrategyManager:
    """Get the global strategy manager instance.
    
    Returns:
        The global strategy manager
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = StrategyManager()
        _global_manager.register_default_strategies()
    
    return _global_manager