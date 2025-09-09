"""Anthropic client implementation."""

from typing import Dict, Any, Optional

from .base_client import BaseLLMClient, LLMError

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude API integration."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        """Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key
            base_url: Optional custom base URL
        """
        if not ANTHROPIC_AVAILABLE:
            raise LLMError("Anthropic package not installed. Run: pip install anthropic")
        
        super().__init__(api_key, base_url)
        
        if not self.api_key:
            raise LLMError("Anthropic API key is required")
        
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_response(
        self, 
        prompt: str, 
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate a response using Anthropic Claude.
        
        Args:
            prompt: The input prompt
            model: Claude model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If the request fails
        """
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise LLMError(f"Anthropic API error: {str(e)}")
    
    def validate_connection(self) -> bool:
        """Validate connection to Anthropic API.
        
        Returns:
            True if connection is successful
            
        Raises:
            LLMError: If connection fails
        """
        try:
            # Test with a minimal request
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return bool(response.content)
            
        except Exception as e:
            raise LLMError(f"Anthropic connection failed: {str(e)}")
    
    def get_available_models(self) -> list[str]:
        """Get list of available Anthropic models.
        
        Returns:
            List of model identifiers
        """
        # Anthropic doesn't provide a models endpoint, return known models
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
        ]
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get Anthropic client information.
        
        Returns:
            Dictionary with client information
        """
        info = super().get_client_info()
        info.update({
            "provider": "Anthropic",
            "default_model": "claude-3-sonnet-20240229",
            "supports_streaming": False,
            "available_models": self.get_available_models(),
        })
        return info