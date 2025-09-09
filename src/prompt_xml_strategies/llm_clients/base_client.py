"""Base abstract class for LLM clients."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMError(Exception):
    """Exception raised by LLM client operations."""
    pass


class BaseLLMClient(ABC):
    """Abstract base class for different LLM provider integrations."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        """Initialize the LLM client.
        
        Args:
            api_key: API key for the provider
            base_url: Base URL for the API endpoint
        """
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        model: str = "default",
        **kwargs
    ) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            model: Model identifier
            **kwargs: Additional model parameters
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If the request fails
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate that the client can connect to the LLM service.
        
        Returns:
            True if connection is successful
            
        Raises:
            LLMError: If connection fails
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models.
        
        Returns:
            List of model identifiers
            
        Raises:
            LLMError: If request fails
        """
        pass
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the client.
        
        Returns:
            Dictionary with client information
        """
        return {
            "client_type": self.__class__.__name__,
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key),
        }