"""OLLAMA client implementation with direct API access."""

import json
import time
from typing import Dict, Any, Optional, List, Union
import requests

from .base_client import BaseLLMClient, LLMError


class OllamaClient(BaseLLMClient):
    """Client for direct OLLAMA API integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434"
    ) -> None:
        """Initialize OLLAMA client.

        Args:
            api_key: Optional API key (typically not required for local OLLAMA)
            base_url: OLLAMA server URL (default: localhost:11434)
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
        top_p: float = 0.9,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        seed: Optional[int] = None,
        stream: bool = False,
        keep_alive: Optional[Union[int, str]] = None,
        format: Optional[str] = None,
        raw: bool = False,
        **kwargs
    ) -> str:
        """Generate a response using OLLAMA generate endpoint.

        Args:
            prompt: The input prompt
            model: Model name (e.g., "llama3.2", "mistral", "codellama")
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate (num_predict)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            repeat_penalty: Penalty for repetition
            seed: Random seed for reproducible outputs
            stream: Whether to stream the response
            keep_alive: How long to keep model in memory (seconds or duration string)
            format: Response format ("json" for structured output)
            raw: Whether to pass prompt directly without template
            **kwargs: Additional OLLAMA parameters

        Returns:
            Generated response text

        Raises:
            LLMError: If the request fails
        """
        try:
            url = f"{self.base_url}/api/generate"

            # Build options dict
            options = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repeat_penalty": repeat_penalty,
            }

            if max_tokens:
                options["num_predict"] = max_tokens
            if seed is not None:
                options["seed"] = seed

            # Add any additional options
            options.update(kwargs)

            # Build payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": options,
                "raw": raw,
            }

            if keep_alive is not None:
                payload["keep_alive"] = keep_alive
            if format:
                payload["format"] = format

            response = self.session.post(url, json=payload, timeout=300)

            if response.status_code != 200:
                raise LLMError(f"OLLAMA API error: {response.status_code} - {response.text}")

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
            raise LLMError(f"Network error connecting to OLLAMA: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response from OLLAMA: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error: {str(e)}")

    def chat_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 0.9,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
        seed: Optional[int] = None,
        stream: bool = False,
        keep_alive: Optional[Union[int, str]] = None,
        format: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a chat response using OLLAMA chat endpoint.

        Args:
            messages: List of chat messages with 'role' and 'content' keys
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            repeat_penalty: Penalty for repetition
            seed: Random seed for reproducible outputs
            stream: Whether to stream the response
            keep_alive: How long to keep model in memory
            format: Response format ("json" for structured output)
            **kwargs: Additional OLLAMA parameters

        Returns:
            Generated response text

        Raises:
            LLMError: If the request fails
        """
        try:
            url = f"{self.base_url}/api/chat"

            # Build options dict
            options = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repeat_penalty": repeat_penalty,
            }

            if max_tokens:
                options["num_predict"] = max_tokens
            if seed is not None:
                options["seed"] = seed

            # Add any additional options
            options.update(kwargs)

            # Build payload
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "options": options,
            }

            if keep_alive is not None:
                payload["keep_alive"] = keep_alive
            if format:
                payload["format"] = format

            response = self.session.post(url, json=payload, timeout=300)

            if response.status_code != 200:
                raise LLMError(f"OLLAMA chat API error: {response.status_code} - {response.text}")

            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'message' in chunk and 'content' in chunk['message']:
                                full_response += chunk['message']['content']
                            if chunk.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
                return full_response
            else:
                # Handle single response
                result = response.json()
                return result.get('message', {}).get('content', '')

        except requests.RequestException as e:
            raise LLMError(f"Network error connecting to OLLAMA chat: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response from OLLAMA chat: {str(e)}")
        except Exception as e:
            raise LLMError(f"Unexpected error in chat: {str(e)}")

    def validate_connection(self) -> bool:
        """Validate connection to OLLAMA server.

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
            raise LLMError(f"Cannot connect to OLLAMA server: {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available models from OLLAMA.

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

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific model.

        Args:
            model_name: Name of the model to inspect

        Returns:
            Dictionary with model information

        Raises:
            LLMError: If request fails
        """
        try:
            url = f"{self.base_url}/api/show"
            payload = {"name": model_name}

            response = self.session.post(url, json=payload)

            if response.status_code != 200:
                raise LLMError(f"Failed to get model info: {response.status_code}")

            return response.json()

        except requests.RequestException as e:
            raise LLMError(f"Error getting model info: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response: {str(e)}")

    def pull_model(self, model_name: str, insecure: bool = False) -> bool:
        """Pull/download a model to the OLLAMA server.

        Args:
            model_name: Name of the model to pull
            insecure: Allow insecure connections

        Returns:
            True if successful

        Raises:
            LLMError: If pull fails
        """
        try:
            url = f"{self.base_url}/api/pull"
            payload = {"name": model_name, "insecure": insecure}

            response = self.session.post(url, json=payload, stream=True)

            if response.status_code != 200:
                raise LLMError(f"Failed to pull model: {response.status_code}")

            # Process streaming pull response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if data.get('status') == 'success':
                            return True
                        elif 'error' in data:
                            raise LLMError(f"Pull error: {data['error']}")
                    except json.JSONDecodeError:
                        continue

            return True

        except requests.RequestException as e:
            raise LLMError(f"Error pulling model: {str(e)}")

    def delete_model(self, model_name: str) -> bool:
        """Delete a model from OLLAMA server.

        Args:
            model_name: Name of the model to delete

        Returns:
            True if successful

        Raises:
            LLMError: If deletion fails
        """
        try:
            url = f"{self.base_url}/api/delete"
            payload = {"name": model_name}

            response = self.session.delete(url, json=payload)

            if response.status_code == 200:
                return True
            else:
                raise LLMError(f"Failed to delete model: {response.status_code}")

        except requests.RequestException as e:
            raise LLMError(f"Error deleting model: {str(e)}")

    def copy_model(self, source: str, destination: str) -> bool:
        """Copy a model with a new name.

        Args:
            source: Source model name
            destination: Destination model name

        Returns:
            True if successful

        Raises:
            LLMError: If copy fails
        """
        try:
            url = f"{self.base_url}/api/copy"
            payload = {"source": source, "destination": destination}

            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                return True
            else:
                raise LLMError(f"Failed to copy model: {response.status_code}")

        except requests.RequestException as e:
            raise LLMError(f"Error copying model: {str(e)}")

    def create_blob(self, file_path: str) -> str:
        """Create a blob from a file for model creation.

        Args:
            file_path: Path to the file to upload

        Returns:
            Blob identifier/hash

        Raises:
            LLMError: If blob creation fails
        """
        try:
            url = f"{self.base_url}/api/blobs"

            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(url, files=files)

            if response.status_code == 201:
                return response.json().get('digest', '')
            else:
                raise LLMError(f"Failed to create blob: {response.status_code}")

        except (FileNotFoundError, IOError) as e:
            raise LLMError(f"File error: {str(e)}")
        except requests.RequestException as e:
            raise LLMError(f"Error creating blob: {str(e)}")

    def get_running_models(self) -> List[Dict[str, Any]]:
        """Get list of currently running models.

        Returns:
            List of running model information

        Raises:
            LLMError: If request fails
        """
        try:
            url = f"{self.base_url}/api/ps"
            response = self.session.get(url)

            if response.status_code != 200:
                raise LLMError(f"Failed to get running models: {response.status_code}")

            data = response.json()
            return data.get('models', [])

        except requests.RequestException as e:
            raise LLMError(f"Error getting running models: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response: {str(e)}")

    def embeddings(
        self,
        input_text: Union[str, List[str]],
        model: str = "nomic-embed-text"
    ) -> List[List[float]]:
        """Generate embeddings for input text.

        Args:
            input_text: Text or list of texts to embed
            model: Embedding model name

        Returns:
            List of embedding vectors

        Raises:
            LLMError: If request fails
        """
        try:
            url = f"{self.base_url}/api/embeddings"

            # Convert single string to list
            if isinstance(input_text, str):
                input_text = [input_text]

            payload = {
                "model": model,
                "prompt": input_text[0] if len(input_text) == 1 else input_text
            }

            response = self.session.post(url, json=payload)

            if response.status_code != 200:
                raise LLMError(f"Embeddings API error: {response.status_code}")

            data = response.json()
            embeddings = data.get('embedding', [])

            # Ensure we return a list of lists
            if embeddings and not isinstance(embeddings[0], list):
                embeddings = [embeddings]

            return embeddings

        except requests.RequestException as e:
            raise LLMError(f"Error generating embeddings: {str(e)}")
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response: {str(e)}")

    def get_client_info(self) -> Dict[str, Any]:
        """Get OLLAMA client information.

        Returns:
            Dictionary with client information
        """
        info = super().get_client_info()
        info.update({
            "provider": "OLLAMA",
            "default_model": "llama3.2",
            "supports_streaming": True,
            "supports_chat": True,
            "supports_embeddings": True,
            "supports_model_management": True,
        })

        try:
            models = self.get_available_models()
            info["available_models"] = models
        except LLMError:
            info["available_models"] = []

        try:
            running_models = self.get_running_models()
            info["running_models"] = [m.get('name', '') for m in running_models]
        except LLMError:
            info["running_models"] = []

        return info