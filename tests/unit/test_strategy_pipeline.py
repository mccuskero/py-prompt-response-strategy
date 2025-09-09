"""Tests for the StrategyPipeline interface and AbstractStrategyPipeline base class."""

import pytest
import logging
from unittest.mock import Mock, MagicMock
from xml.etree.ElementTree import Element

from prompt_xml_strategies.core.strategy_pipeline import StrategyPipeline, AbstractStrategyPipeline
from prompt_xml_strategies.core.exceptions import ValidationError, PipelineError
from prompt_xml_strategies.prompt_strategies.interface import PromptCreationStrategy
from prompt_xml_strategies.response_strategies.interface import ResponseCreationStrategy
from prompt_xml_strategies.xml_output_strategies.interface import XmlOutputStrategy
from prompt_xml_strategies.llm_clients.base_client import BaseLLMClient


class ConcreteStrategyPipeline(AbstractStrategyPipeline):
    """Concrete implementation for testing AbstractStrategyPipeline."""
    
    def _execute_prompt_stage(self, input_data, context=None):
        return "test prompt"
    
    def _execute_llm_stage(self, prompt, model, **kwargs):
        return "test response"
    
    def _execute_response_stage(self, raw_response, context=None):
        return {"result": "success"}
    
    def _execute_xml_stage(self, structured_response, context=None):
        element = Element("test")
        element.text = "test content"
        return element


class TestStrategyPipeline:
    """Test cases for StrategyPipeline interface."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that StrategyPipeline cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StrategyPipeline()
    
    def test_interface_methods_exist(self):
        """Test that all required methods exist in the interface."""
        required_methods = [
            'initialize', 'execute', 'shutdown', 'validate_pipeline', 'get_pipeline_info'
        ]
        
        for method_name in required_methods:
            assert hasattr(StrategyPipeline, method_name)
            method = getattr(StrategyPipeline, method_name)
            assert callable(method)


class TestAbstractStrategyPipeline:
    """Test cases for AbstractStrategyPipeline base class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock strategies and client
        self.mock_prompt_strategy = Mock(spec=PromptCreationStrategy)
        self.mock_response_strategy = Mock(spec=ResponseCreationStrategy)
        self.mock_xml_strategy = Mock(spec=XmlOutputStrategy)
        self.mock_llm_client = Mock(spec=BaseLLMClient)
        
        # Configure mock return values
        self.mock_prompt_strategy.get_strategy_info.return_value = {"name": "TestPromptStrategy"}
        self.mock_response_strategy.get_strategy_info.return_value = {"name": "TestResponseStrategy"}
        self.mock_xml_strategy.get_strategy_info.return_value = {"name": "TestXmlStrategy"}
        self.mock_llm_client.get_client_info.return_value = {"client_type": "TestClient"}
        self.mock_llm_client.validate_connection.return_value = True
        
        # Create concrete pipeline instance
        self.pipeline = ConcreteStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client
        )
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        assert self.pipeline.prompt_strategy == self.mock_prompt_strategy
        assert self.pipeline.response_strategy == self.mock_response_strategy
        assert self.pipeline.xml_strategy == self.mock_xml_strategy
        assert self.pipeline.llm_client == self.mock_llm_client
        assert not self.pipeline._initialized
        assert not self.pipeline._shutdown
    
    def test_initialize_success(self):
        """Test successful pipeline initialization."""
        self.pipeline.initialize()
        
        assert self.pipeline._initialized
        self.mock_llm_client.validate_connection.assert_called_once()
    
    def test_initialize_validation_failure(self):
        """Test initialization failure due to validation error."""
        # Create pipeline with None strategy to trigger validation error
        invalid_pipeline = ConcreteStrategyPipeline(
            None,  # Invalid prompt strategy
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client
        )
        
        with pytest.raises(PipelineError, match="Pipeline initialization failed"):
            invalid_pipeline.initialize()
    
    def test_initialize_llm_connection_failure(self):
        """Test initialization failure due to LLM connection error."""
        self.mock_llm_client.validate_connection.side_effect = Exception("Connection failed")
        
        with pytest.raises(PipelineError, match="Pipeline initialization failed"):
            self.pipeline.initialize()
    
    def test_execute_before_initialization(self):
        """Test that execute fails if pipeline not initialized."""
        with pytest.raises(PipelineError, match="Pipeline must be initialized before execution"):
            self.pipeline.execute({"test": "data"})
    
    def test_execute_after_shutdown(self):
        """Test that execute fails if pipeline is shutdown."""
        self.pipeline.initialize()
        self.pipeline.shutdown()
        
        with pytest.raises(PipelineError, match="Pipeline has been shutdown"):
            self.pipeline.execute({"test": "data"})
    
    def test_execute_success(self):
        """Test successful pipeline execution."""
        self.pipeline.initialize()
        
        result = self.pipeline.execute({"test": "data"})
        
        assert "input_data" in result
        assert "prompt" in result
        assert "raw_response" in result
        assert "structured_response" in result
        assert "xml_element" in result
        assert "xml_string" in result
        assert "pipeline_info" in result
        
        assert result["input_data"] == {"test": "data"}
        assert result["prompt"] == "test prompt"
        assert result["raw_response"] == "test response"
        assert result["structured_response"] == {"result": "success"}
        assert isinstance(result["xml_element"], Element)
        assert result["xml_string"] == "<test>test content</test>"
    
    def test_execute_with_context(self):
        """Test pipeline execution with context."""
        self.pipeline.initialize()
        
        context = {"user": "test_user"}
        result = self.pipeline.execute({"test": "data"}, context=context)
        
        assert result["context"] == context
    
    def test_execute_with_model_and_kwargs(self):
        """Test pipeline execution with model and additional kwargs."""
        self.pipeline.initialize()
        
        result = self.pipeline.execute(
            {"test": "data"},
            model="test-model",
            temperature=0.7,
            max_tokens=100
        )
        
        assert result["pipeline_info"]["current_stage"] is None  # Should be reset after execution
        # Also check that pipeline state is clean
        assert self.pipeline._current_stage is None
        assert self.pipeline._execution_context is None
    
    def test_execute_stage_failure(self):
        """Test pipeline execution failure in a specific stage."""
        self.pipeline.initialize()

        # Mock the strategy to fail by overriding the abstract method
        original_execute_prompt = self.pipeline._execute_prompt_stage
        def failing_execute_prompt(input_data, context=None):
            raise Exception("Prompt generation failed")
        self.pipeline._execute_prompt_stage = failing_execute_prompt

        try:
            with pytest.raises(PipelineError, match="Pipeline execution failed at stage 'prompt'"):
                self.pipeline.execute({"test": "data"})
        finally:
            # Restore original method
            self.pipeline._execute_prompt_stage = original_execute_prompt
    
    def test_shutdown_success(self):
        """Test successful pipeline shutdown."""
        self.pipeline.initialize()
        self.pipeline.shutdown()
        
        assert self.pipeline._shutdown
        assert not self.pipeline._initialized
    
    def test_validate_pipeline_success(self):
        """Test successful pipeline validation."""
        result = self.pipeline.validate_pipeline()
        assert result is True
        self.mock_llm_client.validate_connection.assert_called_once()
    
    def test_validate_pipeline_missing_prompt_strategy(self):
        """Test validation failure with missing prompt strategy."""
        invalid_pipeline = ConcreteStrategyPipeline(
            None,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client
        )
        
        with pytest.raises(ValidationError, match="Prompt strategy is required"):
            invalid_pipeline.validate_pipeline()
    
    def test_validate_pipeline_missing_response_strategy(self):
        """Test validation failure with missing response strategy."""
        invalid_pipeline = ConcreteStrategyPipeline(
            self.mock_prompt_strategy,
            None,
            self.mock_xml_strategy,
            self.mock_llm_client
        )
        
        with pytest.raises(ValidationError, match="Response strategy is required"):
            invalid_pipeline.validate_pipeline()
    
    def test_validate_pipeline_missing_xml_strategy(self):
        """Test validation failure with missing XML strategy."""
        invalid_pipeline = ConcreteStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            None,
            self.mock_llm_client
        )
        
        with pytest.raises(ValidationError, match="XML strategy is required"):
            invalid_pipeline.validate_pipeline()
    
    def test_validate_pipeline_missing_llm_client(self):
        """Test validation failure with missing LLM client."""
        invalid_pipeline = ConcreteStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            None
        )
        
        with pytest.raises(ValidationError, match="LLM client is required"):
            invalid_pipeline.validate_pipeline()
    
    def test_validate_pipeline_llm_connection_failure(self):
        """Test validation failure due to LLM connection error."""
        self.mock_llm_client.validate_connection.side_effect = Exception("Connection failed")
        
        with pytest.raises(ValidationError, match="LLM client validation failed"):
            self.pipeline.validate_pipeline()
    
    def test_get_pipeline_info(self):
        """Test getting pipeline information."""
        info = self.pipeline.get_pipeline_info()
        
        assert info["pipeline_type"] == "ConcreteStrategyPipeline"
        assert info["initialized"] is False
        assert info["shutdown"] is False
        assert info["current_stage"] is None
        assert "prompt_strategy" in info
        assert "response_strategy" in info
        assert "xml_strategy" in info
        assert "llm_client" in info
        assert info["version"] == "1.0.0"
    
    def test_lifecycle_hooks(self):
        """Test that lifecycle hooks can be called without error."""
        self.pipeline.on_prompt_generated("test prompt")
        self.pipeline.on_response_received("test response")
        self.pipeline.on_response_processed({"result": "success"})
        
        xml_element = Element("test")
        self.pipeline.on_xml_generated(xml_element)
        
        # Test error hook
        error = Exception("Test error")
        self.pipeline.on_error(error, "test_stage")
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that AbstractStrategyPipeline cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AbstractStrategyPipeline(
                self.mock_prompt_strategy,
                self.mock_response_strategy,
                self.mock_xml_strategy,
                self.mock_llm_client
            )
    
    def test_logger_initialization(self):
        """Test that logger is properly initialized."""
        custom_logger = logging.getLogger("test_logger")
        pipeline = ConcreteStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client,
            logger=custom_logger
        )
        
        assert pipeline.logger == custom_logger
    
    def test_default_logger_initialization(self):
        """Test that default logger is created when none provided."""
        pipeline = ConcreteStrategyPipeline(
            self.mock_prompt_strategy,
            self.mock_response_strategy,
            self.mock_xml_strategy,
            self.mock_llm_client
        )
        
        assert pipeline.logger.name == "ConcreteStrategyPipeline"
        assert isinstance(pipeline.logger, logging.Logger)
