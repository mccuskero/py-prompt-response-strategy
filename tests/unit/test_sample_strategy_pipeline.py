"""Tests for the SampleStrategyPipeline implementation."""

import pytest
import logging
import time
from unittest.mock import Mock, MagicMock, patch
from xml.etree.ElementTree import Element

from prompt_xml_strategies.strategy_pipelines import SampleStrategyPipeline
from prompt_xml_strategies.core.exceptions import ValidationError, PipelineError
from prompt_xml_strategies.prompt_strategies.interface import PromptCreationStrategy
from prompt_xml_strategies.response_strategies.interface import ResponseCreationStrategy
from prompt_xml_strategies.xml_output_strategies.interface import XmlOutputStrategy
from prompt_xml_strategies.llm_clients.base_client import BaseLLMClient


class TestSampleStrategyPipeline:
    """Test cases for SampleStrategyPipeline implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock strategies and client
        self.mock_prompt_strategy = Mock(spec=PromptCreationStrategy)
        self.mock_response_strategy = Mock(spec=ResponseCreationStrategy)
        self.mock_xml_strategy = Mock(spec=XmlOutputStrategy)
        self.mock_llm_client = Mock(spec=BaseLLMClient)
        
        # Configure mock return values
        self.mock_prompt_strategy.get_strategy_info.return_value = {"name": "TestPromptStrategy"}
        self.mock_prompt_strategy.create_prompt.return_value = "test prompt"
        self.mock_response_strategy.get_strategy_info.return_value = {"name": "TestResponseStrategy"}
        self.mock_response_strategy.process_response.return_value = {"result": "success"}
        self.mock_xml_strategy.get_strategy_info.return_value = {"name": "TestXmlStrategy"}
        xml_element = Element("test")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        self.mock_llm_client.get_client_info.return_value = {"client_type": "TestClient"}
        self.mock_llm_client.validate_connection.return_value = True
        self.mock_llm_client.generate_response.return_value = "test response"
        
        # Create sample pipeline instance
        self.pipeline = SampleStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client
        )
    
    def test_pipeline_initialization_with_default_options(self):
        """Test pipeline initialization with default options."""
        assert self.pipeline.enable_timing is False
        assert self.pipeline.enable_validation is True
        assert self.pipeline.max_retries == 3
        assert self.pipeline.timeout == 120
        assert self.pipeline.retry_delay == 1.0
        assert self.pipeline._execution_count == 0
        assert self.pipeline._error_count == 0
    
    def test_pipeline_initialization_with_custom_options(self):
        """Test pipeline initialization with custom options."""
        options = {
            "enable_timing": True,
            "enable_validation": False,
            "max_retries": 5,
            "timeout": 60,
            "retry_delay": 2.0
        }
        
        pipeline = SampleStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client,
            options=options
        )
        
        assert pipeline.enable_timing is True
        assert pipeline.enable_validation is False
        assert pipeline.max_retries == 5
        assert pipeline.timeout == 60
        assert pipeline.retry_delay == 2.0
    
    def test_initialize_with_timing_enabled(self):
        """Test initialization with timing enabled."""
        options = {"enable_timing": True}
        pipeline = SampleStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client,
            options=options
        )
        
        pipeline.initialize()
        assert pipeline._initialized
    
    def test_execute_prompt_stage_success(self):
        """Test successful prompt stage execution."""
        self.pipeline.initialize()
        
        input_data = {"task": "test"}
        result = self.pipeline._execute_prompt_stage(input_data, None)
        
        assert result == "test prompt"
        self.mock_prompt_strategy.create_prompt.assert_called_once_with(input_data, None)
    
    def test_execute_prompt_stage_with_validation(self):
        """Test prompt stage execution with validation enabled."""
        self.pipeline.enable_validation = True
        self.pipeline.initialize()
        
        input_data = {"task": "test"}
        result = self.pipeline._execute_prompt_stage(input_data, None)
        
        assert result == "test prompt"
    
    def test_execute_prompt_stage_validation_failure(self):
        """Test prompt stage execution with validation failure."""
        self.pipeline.enable_validation = True
        self.pipeline.initialize()
        
        # Test with invalid input data
        with pytest.raises(PipelineError, match="Prompt generation failed"):
            self.pipeline._execute_prompt_stage({}, None)  # Empty dict should fail validation
    
    def test_execute_llm_stage_success(self):
        """Test successful LLM stage execution."""
        self.pipeline.initialize()
        
        self.mock_llm_client.generate_response.return_value = "test response"
        result = self.pipeline._execute_llm_stage("test prompt", "test-model")
        
        assert result == "test response"
        self.mock_llm_client.generate_response.assert_called_once_with("test prompt", model="test-model")
    
    def test_execute_llm_stage_with_retries(self):
        """Test LLM stage execution with retries."""
        self.pipeline.max_retries = 3
        self.pipeline.initialize()
        
        # First two calls fail, third succeeds
        self.mock_llm_client.generate_response.side_effect = [
            Exception("Connection error"),
            Exception("Timeout error"),
            "test response"
        ]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.pipeline._execute_llm_stage("test prompt", "test-model")
        
        assert result == "test response"
        assert self.mock_llm_client.generate_response.call_count == 3
    
    def test_execute_llm_stage_all_retries_fail(self):
        """Test LLM stage execution when all retries fail."""
        self.pipeline.max_retries = 2
        self.pipeline.initialize()
        
        self.mock_llm_client.generate_response.side_effect = Exception("Persistent error")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(PipelineError, match="LLM request failed after 2 attempts"):
                self.pipeline._execute_llm_stage("test prompt", "test-model")
    
    def test_execute_response_stage_success(self):
        """Test successful response stage execution."""
        self.pipeline.initialize()
        
        self.mock_response_strategy.process_response.return_value = {"result": "success"}
        result = self.pipeline._execute_response_stage("raw response", None)
        
        assert result == {"result": "success"}
        self.mock_response_strategy.process_response.assert_called_once_with("raw response", None)
    
    def test_execute_response_stage_with_validation(self):
        """Test response stage execution with validation."""
        self.pipeline.enable_validation = True
        self.pipeline.initialize()
        
        self.mock_response_strategy.process_response.return_value = {"result": "success"}
        result = self.pipeline._execute_response_stage("raw response", None)
        
        assert result == {"result": "success"}
    
    def test_execute_xml_stage_success(self):
        """Test successful XML stage execution."""
        self.pipeline.initialize()
        
        xml_element = Element("test")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        result = self.pipeline._execute_xml_stage({"result": "success"}, None)
        
        assert result == xml_element
        self.mock_xml_strategy.transform_to_xml.assert_called_once_with({"result": "success"}, None)
    
    def test_execute_xml_stage_with_validation(self):
        """Test XML stage execution with validation."""
        self.pipeline.enable_validation = True
        self.pipeline.initialize()
        
        xml_element = Element("test")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        result = self.pipeline._execute_xml_stage({"result": "success"}, None)
        
        assert result == xml_element
    
    def test_lifecycle_hooks(self):
        """Test that lifecycle hooks work correctly."""
        self.pipeline.initialize()
        
        # Test all lifecycle hooks
        self.pipeline.on_prompt_generated("test prompt")
        self.pipeline.on_response_received("test response")
        self.pipeline.on_response_processed({"result": "success"})
        
        xml_element = Element("test")
        self.pipeline.on_xml_generated(xml_element)
        
        # Test error hook
        error = Exception("Test error")
        self.pipeline.on_error(error, "test_stage")
        # Error counting is handled in the execute method, not the hook
    
    def test_execute_with_timing(self):
        """Test pipeline execution with timing enabled."""
        options = {"enable_timing": True}
        pipeline = SampleStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client,
            options=options
        )
        
        pipeline.initialize()
        
        # Mock the strategies to return expected values
        self.mock_prompt_strategy.create_prompt.return_value = "test prompt"
        self.mock_llm_client.generate_response.return_value = "test response"
        self.mock_response_strategy.process_response.return_value = {"result": "success"}
        xml_element = Element("test")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        
        result = pipeline.execute({"test": "data"})
        
        assert result["prompt"] == "test prompt"
        assert result["raw_response"] == "test response"
        assert result["structured_response"] == {"result": "success"}
        assert result["xml_element"] == xml_element
        
        # Check that timing was recorded
        assert pipeline._stage_timings
        assert "prompt" in pipeline._stage_timings
        assert "llm" in pipeline._stage_timings
        assert "response" in pipeline._stage_timings
        assert "xml" in pipeline._stage_timings
    
    def test_execute_without_timing(self):
        """Test pipeline execution without timing."""
        self.pipeline.initialize()
        
        # Mock the strategies to return expected values
        self.mock_prompt_strategy.create_prompt.return_value = "test prompt"
        self.mock_llm_client.generate_response.return_value = "test response"
        self.mock_response_strategy.process_response.return_value = {"result": "success"}
        xml_element = Element("test")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        
        result = self.pipeline.execute({"test": "data"})
        
        assert result["prompt"] == "test prompt"
        assert result["raw_response"] == "test response"
        assert result["structured_response"] == {"result": "success"}
        assert result["xml_element"] == xml_element
        
        # Check that no timing was recorded
        assert not self.pipeline._stage_timings
    
    def test_execution_counting(self):
        """Test that execution counting works correctly."""
        self.pipeline.initialize()
        
        # Mock the strategies
        self.mock_prompt_strategy.create_prompt.return_value = "test prompt"
        self.mock_llm_client.generate_response.return_value = "test response"
        self.mock_response_strategy.process_response.return_value = {"result": "success"}
        xml_element = Element("test")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        
        # Execute multiple times
        self.pipeline.execute({"test": "data1"})
        self.pipeline.execute({"test": "data2"})
        self.pipeline.execute({"test": "data3"})
        
        assert self.pipeline._execution_count == 3
        assert self.pipeline._error_count == 0
    
    def test_error_counting(self):
        """Test that error counting works correctly."""
        self.pipeline.initialize()
        
        # Mock a stage to fail
        self.mock_prompt_strategy.create_prompt.side_effect = Exception("Prompt failed")
        
        with pytest.raises(PipelineError):
            self.pipeline.execute({"test": "data"})
        
        assert self.pipeline._execution_count == 1
        assert self.pipeline._error_count == 1
    
    def test_get_pipeline_info(self):
        """Test getting pipeline information."""
        self.pipeline.initialize()
        
        info = self.pipeline.get_pipeline_info()
        
        assert info["pipeline_type"] == "SampleStrategyPipeline"
        assert info["execution_count"] == 0
        assert info["error_count"] == 0
        assert info["success_rate"] == 1.0
        assert info["average_execution_time"] == 0.0
        assert "features" in info
        assert info["features"]["timing"] is False
        assert info["features"]["validation"] is True
        assert info["features"]["retries"] is True
    
    def test_validation_methods(self):
        """Test validation helper methods."""
        # Test valid input data
        self.pipeline._validate_input_data({"key": "value"})
        
        # Test invalid input data
        with pytest.raises(ValidationError, match="Input data must be a dictionary"):
            self.pipeline._validate_input_data("not a dict")
        
        with pytest.raises(ValidationError, match="Input data cannot be empty"):
            self.pipeline._validate_input_data({})
        
        # Test valid structured response
        self.pipeline._validate_structured_response({"key": "value"})
        
        # Test invalid structured response
        with pytest.raises(ValidationError, match="Structured response must be a dictionary"):
            self.pipeline._validate_structured_response("not a dict")
        
        with pytest.raises(ValidationError, match="Structured response cannot be empty"):
            self.pipeline._validate_structured_response({})
        
        # Test valid XML element
        xml_element = Element("test")
        self.pipeline._validate_xml_element(xml_element)
        
        # Test invalid XML element
        with pytest.raises(ValidationError, match="XML element cannot be None"):
            self.pipeline._validate_xml_element(None)
    
    def test_shutdown_with_statistics(self):
        """Test shutdown with execution statistics."""
        self.pipeline.initialize()
        
        # Execute a few times to generate statistics
        self.mock_prompt_strategy.create_prompt.return_value = "test prompt"
        self.mock_llm_client.generate_response.return_value = "test response"
        self.mock_response_strategy.process_response.return_value = {"result": "success"}
        xml_element = Element("test")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        
        self.pipeline.execute({"test": "data1"})
        self.pipeline.execute({"test": "data2"})
        
        # Shutdown should log statistics
        self.pipeline.shutdown()
        
        assert self.pipeline._shutdown
        assert self.pipeline._execution_count == 2
        assert self.pipeline._error_count == 0
    
    def test_custom_logger(self):
        """Test pipeline with custom logger."""
        custom_logger = logging.getLogger("test_logger")
        pipeline = SampleStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client,
            logger=custom_logger
        )
        
        assert pipeline.logger == custom_logger
