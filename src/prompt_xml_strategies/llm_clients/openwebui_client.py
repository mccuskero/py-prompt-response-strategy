"""OpenWebUI client implementation."""

import json
from typing import Dict, Any, Optional
import requests

from .base_client import BaseLLMClient, LLMError


class OpenWebUIClient(BaseLLMClient):
    """Client for OpenWebUI API integration."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "http://localhost:11434"
    ) -> None:
        """Initialize OpenWebUI client.
        
        Args:
            api_key: Optional API key (if authentication is enabled)
            base_url: OpenWebUI server URL (default: localhost:11434)
        """
        super().__init__(api_key, base_url)
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def generate_response(
        self, 
        prompt: str, 
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Generate a response using OpenWebUI.
        
        Args:
            prompt: The input prompt
            model: Model name (e.g., "llama3.2", "mistral")
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If the request fails
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            # Add any additional parameters
            payload["options"].update(kwargs)
            
            response = self.session.post(url, json=payload)
            
            if response.status_code != 200:
                raise LLMError(f"OpenWebUI API error: {response.status_code} - {response.text}")
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                full_response += chunk['response']
                            if chunk.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
                return full_response
            else:
                # Handle single response
                result = response.json()
                return result.get('response', '')
                
        except requests.RequestException as e:
            raise LLMError(f"Network error connecting to OpenWebUI: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response from OpenWebUI: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")
    
    def validate_connection(self) -> bool:
        """Validate connection to OpenWebUI server.
        
        Returns:
            True if connection is successful
            
        Raises:
            LLMError: If connection fails
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                raise LLMError(f"Connection failed: {response.status_code}")
                
        except requests.RequestException as e:
            raise LLMError(f"Cannot connect to OpenWebUI server: {str(e)}")
    
    def get_available_models(self) -> list[str]:
        """Get list of available models from OpenWebUI.
        
        Returns:
            List of model names
            
        Raises:
            LLMError: If request fails
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = self.session.get(url)
            
            if response.status_code != 200:
                raise LLMError(f"Failed to get models: {response.status_code}")
            
            data = response.json()
            models = []
            
            if 'models' in data:
                for model in data['models']:
                    if 'name' in model:
                        models.append(model['name'])
            
            return models
            
        except requests.RequestException as e:
            raise LLMError(f"Network error getting models: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response: {str(e)}")
    
    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model to the OpenWebUI server.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful
            
        Raises:
            LLMError: If pull fails
        """
        try:
            url = f"{self.base_url}/api/pull"
            payload = {"name": model_name}
            
            response = self.session.post(url, json=payload)
            
            if response.status_code != 200:
                raise LLMError(f"Failed to pull model: {response.status_code}")
            
            return True
            
        except requests.RequestException as e:
            raise LLMError(f"Error pulling model: {str(e)}")
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get OpenWebUI client information.
        
        Returns:
            Dictionary with client information
        """
        info = super().get_client_info()
        info.update({
            "provider": "OpenWebUI",
            "default_model": "llama3.2",
            "supports_streaming": True,
        })
        
        try:
            models = self.get_available_models()
            info["available_models"] = models
        except LLMError:
            info["available_models"] = []
        
        return info