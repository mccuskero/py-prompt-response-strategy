"""Registry for managing and discovering prompt strategies."""

from typing import Dict, List, Optional, Type

from .prompt_strategy import PromptStrategy


class StrategyRegistryError(Exception):
    """Exception raised by strategy registry operations."""
    pass


class StrategyRegistry:
    """Registry for managing and discovering prompt strategies."""
    
    def __init__(self) -> None:
        """Initialize the strategy registry."""
        self._strategies: Dict[str, Type[PromptStrategy]] = {}
        self._instances: Dict[str, PromptStrategy] = {}
    
    def register(self, strategy_class: Type[PromptStrategy], name: Optional[str] = None) -> None:
        """Register a strategy class.
        
        Args:
            strategy_class: The strategy class to register
            name: Optional custom name (defaults to class name)
            
        Raises:
            StrategyRegistryError: If strategy is already registered
        """
        if not issubclass(strategy_class, PromptStrategy):
            raise StrategyRegistryError(
                f"Strategy class must inherit from PromptStrategy: {strategy_class}"
            )
        
        strategy_name = name or strategy_class.__name__
        
        if strategy_name in self._strategies:
            raise StrategyRegistryError(
                f"Strategy '{strategy_name}' is already registered"
            )
        
        self._strategies[strategy_name] = strategy_class
    
    def unregister(self, name: str) -> None:
        """Unregister a strategy.
        
        Args:
            name: The strategy name to unregister
            
        Raises:
            StrategyRegistryError: If strategy is not registered
        """
        if name not in self._strategies:
            raise StrategyRegistryError(f"Strategy '{name}' is not registered")
        
        del self._strategies[name]
        
        # Also remove cached instance if it exists
        if name in self._instances:
            del self._instances[name]
    
    def get_strategy(self, name: str) -> PromptStrategy:
        """Get a strategy instance by name.
        
        Args:
            name: The strategy name
            
        Returns:
            The strategy instance
            
        Raises:
            StrategyRegistryError: If strategy is not registered
        """
        if name not in self._strategies:
            raise StrategyRegistryError(f"Strategy '{name}' is not registered")
        
        # Return cached instance if available
        if name in self._instances:
            return self._instances[name]
        
        # Create new instance
        strategy_class = self._strategies[name]
        instance = strategy_class(name=name)
        self._instances[name] = instance
        
        return instance
    
    def get_strategy_class(self, name: str) -> Type[PromptStrategy]:
        """Get a strategy class by name.
        
        Args:
            name: The strategy name
            
        Returns:
            The strategy class
            
        Raises:
            StrategyRegistryError: If strategy is not registered
        """
        if name not in self._strategies:
            raise StrategyRegistryError(f"Strategy '{name}' is not registered")
        
        return self._strategies[name]
    
    def list_strategies(self) -> List[str]:
        """List all registered strategy names.
        
        Returns:
            List of strategy names
        """
        return list(self._strategies.keys())
    
    def has_strategy(self, name: str) -> bool:
        """Check if a strategy is registered.
        
        Args:
            name: The strategy name
            
        Returns:
            True if strategy is registered
        """
        return name in self._strategies
    
    def get_strategy_info(self, name: str) -> Dict[str, str]:
        """Get information about a registered strategy.
        
        Args:
            name: The strategy name
            
        Returns:
            Dictionary with strategy information
            
        Raises:
            StrategyRegistryError: If strategy is not registered
        """
        if name not in self._strategies:
            raise StrategyRegistryError(f"Strategy '{name}' is not registered")
        
        strategy_class = self._strategies[name]
        
        # Get instance to access description and other properties
        instance = self.get_strategy(name)
        
        return {
            "name": name,
            "class": strategy_class.__name__,
            "module": strategy_class.__module__,
            "description": getattr(instance, 'description', ''),
            "doc": strategy_class.__doc__ or '',
        }
    
    def get_all_strategies_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all registered strategies.
        
        Returns:
            Dictionary mapping strategy names to their info
        """
        return {name: self.get_strategy_info(name) for name in self.list_strategies()}
    
    def clear(self) -> None:
        """Clear all registered strategies."""
        self._strategies.clear()
        self._instances.clear()
    
    def register_built_in_strategies(self) -> None:
        """Register all built-in strategies."""
        # Note: This class is deprecated in favor of StrategyManager
        # No built-in strategies are registered here anymore
        pass
    
    def __len__(self) -> int:
        """Get number of registered strategies."""
        return len(self._strategies)
    
    def __contains__(self, name: str) -> bool:
        """Check if strategy is registered (supports 'in' operator)."""
        return self.has_strategy(name)
    
    def __iter__(self):
        """Iterate over strategy names."""
        return iter(self._strategies.keys())


# Global registry instance
_global_registry: Optional[StrategyRegistry] = None


def get_global_registry() -> StrategyRegistry:
    """Get the global strategy registry instance.
    
    Returns:
        The global registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = StrategyRegistry()
        _global_registry.register_built_in_strategies()
    return _global_registry


def register_strategy(strategy_class: Type[PromptStrategy], name: Optional[str] = None) -> None:
    """Register a strategy in the global registry.
    
    Args:
        strategy_class: The strategy class to register
        name: Optional custom name
    """
    registry = get_global_registry()
    registry.register(strategy_class, name)