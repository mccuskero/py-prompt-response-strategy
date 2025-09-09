"""Interface for prompt creation strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PromptCreationStrategy(ABC):
    """Abstract interface for prompt creation strategies."""
    
    @abstractmethod
    def create_prompt(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a structured prompt from input data.
        
        Args:
            data: Input data for prompt generation
            context: Optional context information
            
        Returns:
            Generated prompt string
            
        Raises:
            ValidationError: If data validation fails
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data against prompt requirements.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if data is valid
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        pass