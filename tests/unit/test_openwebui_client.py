"""Tests for the OpenWebUI client."""

import pytest
from unittest.mock import Mock, patch
import json

from prompt_xml_strategies.llm_clients.openwebui_client import OpenWebUIClient
from prompt_xml_strategies.llm_clients.base_client import LLMError


class TestOpenWebUIClient:
    """Test cases for OpenWebUIClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = OpenWebUIClient(base_url="http://localhost:11434")
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.base_url == "http://localhost:11434"
        assert self.client.api_key is None
        
        # Test with API key
        client_with_key = OpenWebUIClient(api_key="test-key")
        assert client_with_key.api_key == "test-key"
        assert "Authorization" in client_with_key.session.headers
    
    @patch('requests.Session.post')
    def test_generate_response_success(self, mock_post):
        """Test successful response generation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Hello! How can I help you?"}
        mock_post.return_value = mock_response
        
        response = self.client.generate_response("Hello", model="llama3.2")
        
        assert response == "Hello! How can I help you?"
        mock_post.assert_called_once()
        
        # Verify the request payload
        call_args = mock_post.call_args
        assert call_args[1]['json']['model'] == "llama3.2"
        assert call_args[1]['json']['prompt'] == "Hello"
        assert call_args[1]['json']['stream'] is False
    
    @patch('requests.Session.post')
    def test_generate_response_error(self, mock_post):
        """Test response generation with API error."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        with pytest.raises(LLMError) as exc_info:
            self.client.generate_response("Hello")
        
        assert "OpenWebUI API error: 500" in str(exc_info.value)
    
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
                {"name": "mistral:7b"}
            ]
        }
        mock_get.return_value = mock_response
        
        models = self.client.get_available_models()
        
        assert "llama3.2:latest" in models
        assert "mistral:7b" in models
        assert len(models) == 2
    
    def test_get_client_info(self):
        """Test getting client information."""
        info = self.client.get_client_info()
        
        assert info["client_type"] == "OpenWebUIClient"
        assert info["provider"] == "OpenWebUI"
        assert info["base_url"] == "http://localhost:11434"
        assert info["default_model"] == "llama3.2"
        assert info["supports_streaming"] is True