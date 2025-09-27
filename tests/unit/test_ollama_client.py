"""Tests for the OLLAMA client."""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
import io

from prompt_xml_strategies.llm_clients.ollama_client import OllamaClient
from prompt_xml_strategies.llm_clients.base_client import LLMError


class TestOllamaClient:
    """Test cases for OllamaClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = OllamaClient(base_url="http://localhost:11434")

    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.base_url == "http://localhost:11434"
        assert self.client.api_key is None

        # Test with API key
        client_with_key = OllamaClient(api_key="test-key")
        assert client_with_key.api_key == "test-key"
        assert "Authorization" in client_with_key.session.headers

    @patch('requests.Session.post')
    def test_generate_response_success(self, mock_post):
        """Test successful response generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Hello! How can I help you?"}
        mock_post.return_value = mock_response

        response = self.client.generate_response("Hello", model="llama3.2")

        assert response == "Hello! How can I help you?"
        mock_post.assert_called_once()

        # Verify the request payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == "llama3.2"
        assert payload['prompt'] == "Hello"
        assert payload['stream'] is False
        assert payload['raw'] is False

    @patch('requests.Session.post')
    def test_generate_response_with_options(self, mock_post):
        """Test response generation with various options."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Structured response"}
        mock_post.return_value = mock_response

        response = self.client.generate_response(
            "Hello",
            model="llama3.2",
            temperature=0.5,
            max_tokens=100,
            top_p=0.8,
            seed=42,
            format="json",
            keep_alive=300,
            raw=True
        )

        assert response == "Structured response"
        call_args = mock_post.call_args
        payload = call_args[1]['json']

        assert payload['options']['temperature'] == 0.5
        assert payload['options']['num_predict'] == 100
        assert payload['options']['top_p'] == 0.8
        assert payload['options']['seed'] == 42
        assert payload['format'] == "json"
        assert payload['keep_alive'] == 300
        assert payload['raw'] is True

    @patch('requests.Session.post')
    def test_generate_response_streaming(self, mock_post):
        """Test streaming response generation."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'{"response": " there", "done": false}',
            b'{"response": "!", "done": true}'
        ]
        mock_post.return_value = mock_response

        response = self.client.generate_response("Hello", stream=True)

        assert response == "Hello there!"

    @patch('requests.Session.post')
    def test_generate_response_error(self, mock_post):
        """Test response generation with API error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.generate_response("Hello")

        assert "OLLAMA API error: 500" in str(exc_info.value)

    @patch('requests.Session.post')
    def test_chat_response_success(self, mock_post):
        """Test successful chat response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "I'm doing well, thank you!"}
        }
        mock_post.return_value = mock_response

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]

        response = self.client.chat_response(messages, model="llama3.2")

        assert response == "I'm doing well, thank you!"
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == "llama3.2"
        assert payload['messages'] == messages

    @patch('requests.Session.post')
    def test_chat_response_streaming(self, mock_post):
        """Test streaming chat response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"message": {"content": "I\'m"}, "done": false}',
            b'{"message": {"content": " doing"}, "done": false}',
            b'{"message": {"content": " well!"}, "done": true}'
        ]
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "How are you?"}]
        response = self.client.chat_response(messages, stream=True)

        assert response == "I'm doing well!"

    @patch('requests.Session.post')
    def test_chat_response_error(self, mock_post):
        """Test chat response with API error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.chat_response([{"role": "user", "content": "Hello"}])

        assert "OLLAMA chat API error: 400" in str(exc_info.value)

    @patch('requests.Session.get')
    def test_validate_connection_success(self, mock_get):
        """Test successful connection validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert self.client.validate_connection() is True
        mock_get.assert_called_once_with(f"{self.client.base_url}/api/tags", timeout=10)

    @patch('requests.Session.get')
    def test_validate_connection_failure(self, mock_get):
        """Test connection validation failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.validate_connection()

        assert "Connection failed: 404" in str(exc_info.value)

    @patch('requests.Session.get')
    def test_get_available_models(self, mock_get):
        """Test getting available models."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:latest"},
                {"name": "mistral:7b"},
                {"name": "codellama:13b"}
            ]
        }
        mock_get.return_value = mock_response

        models = self.client.get_available_models()

        assert "llama3.2:latest" in models
        assert "mistral:7b" in models
        assert "codellama:13b" in models
        assert len(models) == 3

    @patch('requests.Session.get')
    def test_get_available_models_error(self, mock_get):
        """Test getting available models with error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.get_available_models()

        assert "Failed to get models: 500" in str(exc_info.value)

    @patch('requests.Session.post')
    def test_get_model_info_success(self, mock_post):
        """Test getting model information."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "modelfile": "FROM llama3.2",
            "parameters": "temperature 0.7",
            "template": "{{ .Prompt }}",
            "details": {
                "format": "gguf",
                "family": "llama",
                "families": ["llama"],
                "parameter_size": "7B",
                "quantization_level": "Q4_0"
            }
        }
        mock_post.return_value = mock_response

        info = self.client.get_model_info("llama3.2")

        assert "modelfile" in info
        assert "parameters" in info
        assert info["details"]["family"] == "llama"

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['name'] == "llama3.2"

    @patch('requests.Session.post')
    def test_pull_model_success(self, mock_post):
        """Test successful model pulling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"status": "pulling manifest"}',
            b'{"status": "downloading"}',
            b'{"status": "success"}'
        ]
        mock_post.return_value = mock_response

        result = self.client.pull_model("llama3.2")

        assert result is True
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['name'] == "llama3.2"
        assert payload['insecure'] is False

    @patch('requests.Session.post')
    def test_pull_model_error(self, mock_post):
        """Test model pulling with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.pull_model("nonexistent-model")

        assert "Failed to pull model: 400" in str(exc_info.value)

    @patch('requests.Session.delete')
    def test_delete_model_success(self, mock_delete):
        """Test successful model deletion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        result = self.client.delete_model("llama3.2")

        assert result is True
        call_args = mock_delete.call_args
        payload = call_args[1]['json']
        assert payload['name'] == "llama3.2"

    @patch('requests.Session.delete')
    def test_delete_model_error(self, mock_delete):
        """Test model deletion with error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_delete.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.delete_model("nonexistent-model")

        assert "Failed to delete model: 404" in str(exc_info.value)

    @patch('requests.Session.post')
    def test_copy_model_success(self, mock_post):
        """Test successful model copying."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.client.copy_model("llama3.2", "my-custom-llama")

        assert result is True
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['source'] == "llama3.2"
        assert payload['destination'] == "my-custom-llama"

    @patch('requests.Session.post')
    def test_copy_model_error(self, mock_post):
        """Test model copying with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.copy_model("source", "dest")

        assert "Failed to copy model: 400" in str(exc_info.value)

    @patch('builtins.open', new_callable=mock_open, read_data=b"test file content")
    @patch('requests.Session.post')
    def test_create_blob_success(self, mock_post, mock_file):
        """Test successful blob creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"digest": "sha256:abcd1234"}
        mock_post.return_value = mock_response

        digest = self.client.create_blob("/path/to/file")

        assert digest == "sha256:abcd1234"
        mock_post.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_create_blob_file_error(self, mock_file):
        """Test blob creation with file error."""
        with pytest.raises(LLMError) as exc_info:
            self.client.create_blob("/nonexistent/file")

        assert "File error: File not found" in str(exc_info.value)

    @patch('requests.Session.get')
    def test_get_running_models(self, mock_get):
        """Test getting running models."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {
                    "name": "llama3.2:latest",
                    "digest": "sha256:abcd1234",
                    "size": 4661224676,
                    "expires_at": "2024-01-01T12:00:00Z"
                }
            ]
        }
        mock_get.return_value = mock_response

        running_models = self.client.get_running_models()

        assert len(running_models) == 1
        assert running_models[0]["name"] == "llama3.2:latest"
        assert running_models[0]["size"] == 4661224676

    @patch('requests.Session.post')
    def test_embeddings_single_text(self, mock_post):
        """Test embeddings generation for single text."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        mock_post.return_value = mock_response

        embeddings = self.client.embeddings("Hello world", model="nomic-embed-text")

        assert len(embeddings) == 1
        assert embeddings[0] == [0.1, 0.2, 0.3, 0.4, 0.5]

        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == "nomic-embed-text"
        assert payload['prompt'] == "Hello world"

    @patch('requests.Session.post')
    def test_embeddings_multiple_texts(self, mock_post):
        """Test embeddings generation for multiple texts."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embedding": [[0.1, 0.2], [0.3, 0.4]]
        }
        mock_post.return_value = mock_response

        texts = ["Hello", "World"]
        embeddings = self.client.embeddings(texts)

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]

    @patch('requests.Session.post')
    def test_embeddings_error(self, mock_post):
        """Test embeddings generation with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.embeddings("Hello")

        assert "Embeddings API error: 400" in str(exc_info.value)

    def test_get_client_info(self):
        """Test getting client information."""
        with patch.object(self.client, 'get_available_models', return_value=["llama3.2", "mistral"]):
            with patch.object(self.client, 'get_running_models', return_value=[{"name": "llama3.2"}]):
                info = self.client.get_client_info()

        assert info["client_type"] == "OllamaClient"
        assert info["provider"] == "OLLAMA"
        assert info["base_url"] == "http://localhost:11434"
        assert info["default_model"] == "llama3.2"
        assert info["supports_streaming"] is True
        assert info["supports_chat"] is True
        assert info["supports_embeddings"] is True
        assert info["supports_model_management"] is True
        assert "llama3.2" in info["available_models"]
        assert "llama3.2" in info["running_models"]

    def test_get_client_info_with_errors(self):
        """Test getting client information when API calls fail."""
        with patch.object(self.client, 'get_available_models', side_effect=LLMError("API error")):
            with patch.object(self.client, 'get_running_models', side_effect=LLMError("API error")):
                info = self.client.get_client_info()

        assert info["available_models"] == []
        assert info["running_models"] == []

    @patch('requests.Session.post')
    def test_network_error_handling(self, mock_post):
        """Test handling of network errors."""
        import requests
        mock_post.side_effect = requests.ConnectionError("Connection failed")

        with pytest.raises(LLMError) as exc_info:
            self.client.generate_response("Hello")

        assert "Network error connecting to OLLAMA" in str(exc_info.value)

    @patch('requests.Session.post')
    def test_json_decode_error_handling(self, mock_post):
        """Test handling of JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        mock_post.return_value = mock_response

        with pytest.raises(LLMError) as exc_info:
            self.client.generate_response("Hello")

        assert "Invalid JSON response from OLLAMA" in str(exc_info.value)

    @patch('requests.Session.post')
    def test_streaming_with_invalid_json(self, mock_post):
        """Test streaming response with invalid JSON lines."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'invalid json line',
            b'{"response": " World", "done": true}'
        ]
        mock_post.return_value = mock_response

        response = self.client.generate_response("Hello", stream=True)

        # Should skip invalid JSON and continue
        assert response == "Hello World"

    def test_keep_alive_parameter_types(self):
        """Test different keep_alive parameter types."""
        with patch('requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "OK"}
            mock_post.return_value = mock_response

            # Test with integer (seconds)
            self.client.generate_response("Hello", keep_alive=300)
            call_args = mock_post.call_args
            assert call_args[1]['json']['keep_alive'] == 300

            # Test with string (duration)
            self.client.generate_response("Hello", keep_alive="5m")
            call_args = mock_post.call_args
            assert call_args[1]['json']['keep_alive'] == "5m"