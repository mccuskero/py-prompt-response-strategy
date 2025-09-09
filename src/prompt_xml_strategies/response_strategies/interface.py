"""Interface for response creation strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ResponseCreationStrategy(ABC):
    """Abstract interface for response creation strategies."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate processed response against schema.
        
        Args:
            response: Processed response data
            
        Returns:
            True if response is valid
            
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