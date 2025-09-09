"""Tests for the QAStrategyPipeline implementation."""

import pytest
import logging
import time
from unittest.mock import Mock, MagicMock, patch
from xml.etree.ElementTree import Element

from prompt_xml_strategies.strategy_pipelines import QAStrategyPipeline
from prompt_xml_strategies.core.exceptions import ValidationError, PipelineError
from prompt_xml_strategies.prompt_strategies.qa_prompt_strategy import QAPromptStrategy
from prompt_xml_strategies.response_strategies.qa_response_strategy import QAResponseStrategy
from prompt_xml_strategies.xml_output_strategies.qa_xml_output_strategy import QAXmlOutputStrategy
from prompt_xml_strategies.llm_clients.base_client import BaseLLMClient


class TestQAStrategyPipeline:
    """Test cases for QAStrategyPipeline implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock strategies and client
        self.mock_prompt_strategy = Mock(spec=QAPromptStrategy)
        self.mock_response_strategy = Mock(spec=QAResponseStrategy)
        self.mock_xml_strategy = Mock(spec=QAXmlOutputStrategy)
        self.mock_llm_client = Mock(spec=BaseLLMClient)
        
        # Configure mock return values
        self.mock_prompt_strategy.get_strategy_info.return_value = {"name": "QAPromptStrategy"}
        self.mock_prompt_strategy.create_prompt.return_value = "test qa prompt"
        self.mock_response_strategy.get_strategy_info.return_value = {"name": "QAResponseStrategy"}
        self.mock_response_strategy.process_response.return_value = {
            "answer": "Test answer",
            "confidence": 0.9,
            "sources": [],
            "follow_up_questions": []
        }
        self.mock_xml_strategy.get_strategy_info.return_value = {"name": "QAXmlOutputStrategy"}
        xml_element = Element("qa_response")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        self.mock_xml_strategy.validate_xml.return_value = True
        self.mock_llm_client.get_client_info.return_value = {"client_type": "TestClient"}
        self.mock_llm_client.validate_connection.return_value = True
        self.mock_llm_client.generate_response.return_value = "test response"
        
        # Create sample pipeline instance
        self.pipeline = QAStrategyPipeline(
            prompt_strategy=self.mock_prompt_strategy,
            response_strategy=self.mock_response_strategy,
            xml_strategy=self.mock_xml_strategy,
            llm_client=self.mock_llm_client
        )
    
    def test_pipeline_initialization_with_default_strategies(self):
        """Test pipeline initialization with default strategies."""
        pipeline = QAStrategyPipeline(llm_client=self.mock_llm_client)
        
        assert isinstance(pipeline.prompt_strategy, QAPromptStrategy)
        assert isinstance(pipeline.response_strategy, QAResponseStrategy)
        assert isinstance(pipeline.xml_strategy, QAXmlOutputStrategy)
        assert pipeline.qa_config["conversation_context"] is True
        assert pipeline.qa_config["response_enhancement"] is True
        assert pipeline.qa_config["xml_validation"] is True
        assert pipeline.qa_config["metadata_tracking"] is True
    
    def test_pipeline_initialization_with_custom_options(self):
        """Test pipeline initialization with custom options."""
        options = {
            "enable_timing": True,
            "enable_validation": False,
            "max_retries": 5,
            "timeout": 60,
            "retry_delay": 2.0,
            "conversation_context": False,
            "response_enhancement": False
        }
        
        pipeline = QAStrategyPipeline(
            llm_client=self.mock_llm_client,
            options=options
        )
        
        assert pipeline.enable_timing is True
        assert pipeline.enable_validation is False
        assert pipeline.max_retries == 5
        assert pipeline.timeout == 60
        assert pipeline.retry_delay == 2.0
        assert pipeline.qa_config["conversation_context"] is False
        assert pipeline.qa_config["response_enhancement"] is False
    
    def test_pipeline_initialization_requires_llm_client(self):
        """Test that pipeline initialization requires an LLM client."""
        with pytest.raises(ValueError, match="LLM client is required for QA pipeline"):
            QAStrategyPipeline()
    
    def test_validate_input_data_with_question(self):
        """Test input validation with question field."""
        input_data = {"question": "What is AI?"}
        self.pipeline._validate_input_data(input_data)
    
    def test_validate_input_data_with_user_input(self):
        """Test input validation with user_input field."""
        input_data = {"user_input": "Tell me about machine learning"}
        self.pipeline._validate_input_data(input_data)
    
    def test_validate_input_data_with_conversation_history(self):
        """Test input validation with conversation history."""
        input_data = {
            "question": "What is AI?",
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        self.pipeline._validate_input_data(input_data)
    
    def test_validate_input_data_missing_required_fields(self):
        """Test input validation with missing required fields."""
        with pytest.raises(ValidationError, match="QA pipeline requires either 'question' or 'user_input' field"):
            self.pipeline._validate_input_data({"other_field": "value"})
    
    def test_validate_input_data_invalid_question_type(self):
        """Test input validation with invalid question type."""
        with pytest.raises(ValidationError, match="Question must be a string"):
            self.pipeline._validate_input_data({"question": 123})
    
    def test_validate_input_data_invalid_conversation_history(self):
        """Test input validation with invalid conversation history."""
        with pytest.raises(ValidationError, match="Conversation history must be a list"):
            self.pipeline._validate_input_data({
                "question": "What is AI?",
                "conversation_history": "not a list"
            })
    
    def test_validate_structured_response_valid(self):
        """Test structured response validation with valid data."""
        response = {
            "answer": "AI is artificial intelligence",
            "confidence": 0.9,
            "sources": [{"title": "AI Guide", "url": "https://example.com"}],
            "follow_up_questions": ["What are the types of AI?"]
        }
        self.pipeline._validate_structured_response(response)
    
    def test_validate_structured_response_missing_answer(self):
        """Test structured response validation with missing answer."""
        with pytest.raises(ValidationError, match="QA response must contain an 'answer' field"):
            self.pipeline._validate_structured_response({"confidence": 0.9})
    
    def test_validate_structured_response_invalid_confidence(self):
        """Test structured response validation with invalid confidence."""
        with pytest.raises(ValidationError, match="Confidence must be a number between 0 and 1"):
            self.pipeline._validate_structured_response({
                "answer": "Test answer",
                "confidence": 1.5
            })
    
    def test_execute_prompt_stage_success(self):
        """Test successful prompt stage execution."""
        self.pipeline.initialize()
        
        input_data = {"question": "What is AI?"}
        result = self.pipeline._execute_prompt_stage(input_data, None)
        
        assert result == "test qa prompt"
        self.mock_prompt_strategy.create_prompt.assert_called_once_with(input_data, None)
    
    def test_execute_response_stage_success(self):
        """Test successful response stage execution."""
        self.pipeline.initialize()
        
        result = self.pipeline._execute_response_stage("test response", None)
        
        assert result["answer"] == "Test answer"
        assert result["confidence"] == 0.9
        self.mock_response_strategy.process_response.assert_called_once_with("test response", None)
    
    def test_execute_xml_stage_success(self):
        """Test successful XML stage execution."""
        self.pipeline.initialize()
        
        structured_response = {"answer": "Test answer", "confidence": 0.9}
        result = self.pipeline._execute_xml_stage(structured_response, None)
        
        assert result.tag == "qa_response"
        self.mock_xml_strategy.transform_to_xml.assert_called_once_with(structured_response, None)
        self.mock_xml_strategy.validate_xml.assert_called_once_with(result)
    
    def test_execute_xml_stage_validation_disabled(self):
        """Test XML stage execution with validation disabled."""
        self.pipeline.qa_config["xml_validation"] = False
        self.pipeline.initialize()
        
        structured_response = {"answer": "Test answer", "confidence": 0.9}
        result = self.pipeline._execute_xml_stage(structured_response, None)
        
        assert result.tag == "qa_response"
        self.mock_xml_strategy.validate_xml.assert_not_called()
    
    def test_execute_with_timing(self):
        """Test pipeline execution with timing enabled."""
        self.pipeline.initialize()
        
        # Mock the strategies to return expected values
        self.mock_prompt_strategy.create_prompt.return_value = "test qa prompt"
        self.mock_llm_client.generate_response.return_value = "test response"
        self.mock_response_strategy.process_response.return_value = {
            "answer": "Test answer",
            "confidence": 0.9
        }
        xml_element = Element("qa_response")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        
        result = self.pipeline.execute({"question": "What is AI?"})
        
        assert result["prompt"] == "test qa prompt"
        assert result["raw_response"] == "test response"
        assert result["structured_response"]["answer"] == "Test answer"
        assert result["xml_element"] == xml_element
        
        # Check that timing was recorded
        assert self.pipeline._stage_timings
        assert "prompt" in self.pipeline._stage_timings
        assert "llm" in self.pipeline._stage_timings
        assert "response" in self.pipeline._stage_timings
        assert "xml" in self.pipeline._stage_timings
    
    def test_get_pipeline_info(self):
        """Test getting pipeline information."""
        self.pipeline.initialize()
        
        info = self.pipeline.get_pipeline_info()
        
        assert info["pipeline_type"] == "QAStrategyPipeline"
        assert "qa_config" in info
        assert "strategies" in info
        assert "features" in info
        assert info["qa_config"]["conversation_context"] is True
        assert info["qa_config"]["response_enhancement"] is True
        assert info["qa_config"]["xml_validation"] is True
        assert info["qa_config"]["metadata_tracking"] is True
    
    def test_get_qa_metrics(self):
        """Test getting QA-specific metrics."""
        self.pipeline.initialize()
        
        # Execute a few times to generate metrics
        self.mock_prompt_strategy.create_prompt.return_value = "test qa prompt"
        self.mock_llm_client.generate_response.return_value = "test response"
        self.mock_response_strategy.process_response.return_value = {
            "answer": "Test answer",
            "confidence": 0.9
        }
        xml_element = Element("qa_response")
        self.mock_xml_strategy.transform_to_xml.return_value = xml_element
        
        self.pipeline.execute({"question": "What is AI?"})
        self.pipeline.execute({"question": "What is ML?"})
        
        metrics = self.pipeline.get_qa_metrics()
        
        assert metrics["total_questions_processed"] == 2
        assert metrics["successful_qa_workflows"] == 2
        assert metrics["failed_qa_workflows"] == 0
        assert metrics["qa_success_rate"] == 1.0
        assert "qa_configuration" in metrics
    
    def test_qa_configuration_updates(self):
        """Test that QA configuration can be updated through options."""
        options = {
            "conversation_context": False,
            "response_enhancement": False,
            "xml_validation": False,
            "metadata_tracking": False
        }
        
        pipeline = QAStrategyPipeline(
            llm_client=self.mock_llm_client,
            options=options
        )
        
        assert pipeline.qa_config["conversation_context"] is False
        assert pipeline.qa_config["response_enhancement"] is False
        assert pipeline.qa_config["xml_validation"] is False
        assert pipeline.qa_config["metadata_tracking"] is False
    
    def test_error_handling_in_prompt_stage(self):
        """Test error handling in prompt stage."""
        self.pipeline.initialize()
        
        self.mock_prompt_strategy.create_prompt.side_effect = Exception("Prompt generation failed")
        
        with pytest.raises(PipelineError, match="QA prompt generation failed"):
            self.pipeline._execute_prompt_stage({"question": "What is AI?"}, None)
    
    def test_error_handling_in_response_stage(self):
        """Test error handling in response stage."""
        self.pipeline.initialize()
        
        self.mock_response_strategy.process_response.side_effect = Exception("Response processing failed")
        
        with pytest.raises(PipelineError, match="QA response processing failed"):
            self.pipeline._execute_response_stage("test response", None)
    
    def test_error_handling_in_xml_stage(self):
        """Test error handling in XML stage."""
        self.pipeline.initialize()
        
        self.mock_xml_strategy.transform_to_xml.side_effect = Exception("XML generation failed")
        
        with pytest.raises(PipelineError, match="QA XML generation failed"):
            self.pipeline._execute_xml_stage({"answer": "Test answer"}, None)
    
    def test_xml_validation_failure(self):
        """Test XML validation failure handling."""
        self.pipeline.initialize()
        
        self.mock_xml_strategy.validate_xml.return_value = False
        
        with pytest.raises(PipelineError, match="Generated XML failed validation against XSD schema"):
            self.pipeline._execute_xml_stage({"answer": "Test answer"}, None)
