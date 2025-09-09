"""Tests for the pipeline system."""

import pytest
from unittest.mock import Mock, patch
from xml.etree.ElementTree import Element

from prompt_xml_strategies.core.pipeline import TripleStrategyPipeline
from prompt_xml_strategies.core.exceptions import ValidationError, PipelineError
from prompt_xml_strategies.prompt_strategies import SimplePromptCreationStrategy
from prompt_xml_strategies.response_strategies import SimpleResponseCreationStrategy
from prompt_xml_strategies.xml_output_strategies import SimpleXmlOutputStrategy


class TestTripleStrategyPipeline:
    """Test cases for TripleStrategyPipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.prompt_strategy = SimplePromptCreationStrategy()
        self.response_strategy = SimpleResponseCreationStrategy()
        self.xml_strategy = SimpleXmlOutputStrategy()
        
        # Mock LLM client
        self.llm_client = Mock()
        self.llm_client.generate_response.return_value = '{"result": "success", "value": 42}'
        self.llm_client.validate_connection.return_value = True
        self.llm_client.get_client_info.return_value = {
            "client_type": "MockClient",
            "provider": "Mock"
        }
        
        self.pipeline = TripleStrategyPipeline(
            prompt_strategy=self.prompt_strategy,
            response_strategy=self.response_strategy,
            xml_strategy=self.xml_strategy,
            llm_client=self.llm_client
        )
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        assert self.pipeline.prompt_strategy is self.prompt_strategy
        assert self.pipeline.response_strategy is self.response_strategy
        assert self.pipeline.xml_strategy is self.xml_strategy
        assert self.pipeline.llm_client is self.llm_client
    
    def test_validate_pipeline_success(self):
        """Test successful pipeline validation."""
        assert self.pipeline.validate_pipeline() is True
        self.llm_client.validate_connection.assert_called_once()
    
    def test_validate_pipeline_missing_prompt_strategy(self):
        """Test pipeline validation with missing prompt strategy."""
        pipeline = TripleStrategyPipeline(
            prompt_strategy=None,
            response_strategy=self.response_strategy,
            xml_strategy=self.xml_strategy,
            llm_client=self.llm_client
        )
        
        with pytest.raises(ValidationError, match="Prompt strategy is required"):
            pipeline.validate_pipeline()
    
    def test_validate_pipeline_missing_response_strategy(self):
        """Test pipeline validation with missing response strategy."""
        pipeline = TripleStrategyPipeline(
            prompt_strategy=self.prompt_strategy,
            response_strategy=None,
            xml_strategy=self.xml_strategy,
            llm_client=self.llm_client
        )
        
        with pytest.raises(ValidationError, match="Response strategy is required"):
            pipeline.validate_pipeline()
    
    def test_validate_pipeline_missing_xml_strategy(self):
        """Test pipeline validation with missing XML strategy."""
        pipeline = TripleStrategyPipeline(
            prompt_strategy=self.prompt_strategy,
            response_strategy=self.response_strategy,
            xml_strategy=None,
            llm_client=self.llm_client
        )
        
        with pytest.raises(ValidationError, match="XML strategy is required"):
            pipeline.validate_pipeline()
    
    def test_validate_pipeline_missing_llm_client(self):
        """Test pipeline validation with missing LLM client."""
        pipeline = TripleStrategyPipeline(
            prompt_strategy=self.prompt_strategy,
            response_strategy=self.response_strategy,
            xml_strategy=self.xml_strategy,
            llm_client=None
        )
        
        with pytest.raises(ValidationError, match="LLM client is required"):
            pipeline.validate_pipeline()
    
    def test_validate_pipeline_llm_connection_failure(self):
        """Test pipeline validation with LLM connection failure."""
        self.llm_client.validate_connection.side_effect = Exception("Connection failed")
        
        with pytest.raises(ValidationError, match="LLM client validation failed"):
            self.pipeline.validate_pipeline()
    
    def test_execute_pipeline_success(self):
        """Test successful pipeline execution."""
        input_data = {"task": "test", "content": "hello"}
        context = {"user": "john"}
        
        result = self.pipeline.execute(input_data, context, model="test-model")
        
        # Verify all stages completed
        assert result["input_data"] == input_data
        assert result["context"] == context
        assert "Input Data:" in result["prompt"]
        assert result["raw_response"] == '{"result": "success", "value": 42}'
        assert result["structured_response"]["result"] == "success"
        assert result["structured_response"]["value"] == 42
        assert result["xml_element"].tag == "response"
        assert "<response" in result["xml_string"]
        assert "pipeline_info" in result
        
        # Verify LLM client was called correctly
        self.llm_client.generate_response.assert_called_once()
        call_args = self.llm_client.generate_response.call_args
        assert call_args[1]["model"] == "test-model"
    
    def test_execute_pipeline_llm_failure(self):
        """Test pipeline execution with LLM failure."""
        self.llm_client.generate_response.side_effect = Exception("LLM error")
        
        input_data = {"task": "test"}
        
        with pytest.raises(PipelineError, match="Pipeline execution failed"):
            self.pipeline.execute(input_data)
    
    def test_create_prompt_only(self):
        """Test creating prompt only."""
        input_data = {"task": "test", "content": "hello"}
        
        prompt = self.pipeline.create_prompt_only(input_data)
        
        assert "Input Data:" in prompt
        assert "test" in prompt
        assert "hello" in prompt
    
    def test_process_response_only(self):
        """Test processing response only."""
        raw_response = '{"status": "ok", "data": ["a", "b"]}'
        
        result = self.pipeline.process_response_only(raw_response)
        
        assert result["status"] == "ok"
        assert result["data"] == ["a", "b"]
    
    def test_create_xml_only(self):
        """Test creating XML only."""
        response_data = {"result": "success", "value": 42}
        
        xml_element = self.pipeline.create_xml_only(response_data)
        
        assert xml_element.tag == "response"
        assert xml_element.find("result").text == "success"
        assert xml_element.find("value").text == "42"
    
    def test_get_pipeline_info(self):
        """Test getting pipeline info."""
        info = self.pipeline.get_pipeline_info()
        
        assert "prompt_strategy" in info
        assert "response_strategy" in info
        assert "xml_strategy" in info
        assert "llm_client" in info
        assert info["pipeline_type"] == "TripleStrategyPipeline"
        assert info["version"] == "1.0.0"
        
        # Verify strategy info is included
        assert info["prompt_strategy"]["name"] == "SimplePromptCreationStrategy"
        assert info["response_strategy"]["name"] == "SimpleResponseCreationStrategy"
        assert info["xml_strategy"]["name"] == "SimpleXmlOutputStrategy"