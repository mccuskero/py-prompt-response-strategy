"""QA Strategy Pipeline implementation for Question-Answer workflows."""

from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element
import logging
import time

from ..core.strategy_pipeline import AbstractStrategyPipeline
from ..prompt_strategies.qa_prompt_strategy import QAPromptStrategy
from ..response_strategies.qa_response_strategy import QAResponseStrategy
from ..xml_output_strategies.qa_xml_output_strategy import QAXmlOutputStrategy
from ..llm_clients.base_client import BaseLLMClient
from ..core.exceptions import PipelineError, ValidationError


class QAStrategyPipeline(AbstractStrategyPipeline):
    """Specialized pipeline for Question-Answer workflows.
    
    This pipeline combines the QA prompt strategy, QA response strategy,
    and QA XML output strategy to create a complete Q&A processing workflow.
    
    Features:
    - Optimized for conversational Q&A interactions
    - Schema-validated prompt generation and response processing
    - XSD-validated XML output generation
    - Enhanced logging for Q&A-specific operations
    - Performance timing and metrics
    - Custom validation for Q&A data structures
    - Retry mechanisms for LLM requests
    - Configurable behavior through options
    """
    
    def __init__(
        self,
        prompt_strategy: Optional[QAPromptStrategy] = None,
        response_strategy: Optional[QAResponseStrategy] = None,
        xml_strategy: Optional[QAXmlOutputStrategy] = None,
        llm_client: Optional[BaseLLMClient] = None,
        options: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the QA pipeline with optional configuration.
        
        Args:
            prompt_strategy: QA prompt strategy (uses default if None)
            response_strategy: QA response strategy (uses default if None)
            xml_strategy: QA XML output strategy (uses default if None)
            llm_client: LLM client for generating responses (required)
            options: Optional configuration dictionary
            logger: Optional logger for pipeline operations
        """
        # Set default strategies if not provided
        if prompt_strategy is None:
            prompt_strategy = QAPromptStrategy()
        if response_strategy is None:
            response_strategy = QAResponseStrategy()
        if xml_strategy is None:
            xml_strategy = QAXmlOutputStrategy()
        
        if llm_client is None:
            raise ValueError("LLM client is required for QA pipeline")
        
        # Initialize with default options for QA workflows
        default_options = {
            "enable_timing": True,
            "enable_validation": True,
            "max_retries": 3,
            "timeout": 120,
            "retry_delay": 1.0,
            "log_level": "INFO"
        }
        
        if options:
            default_options.update(options)
        
        super().__init__(
            prompt_strategy=prompt_strategy,
            response_strategy=response_strategy,
            xml_strategy=xml_strategy,
            llm_client=llm_client,
            logger=logger
        )
        
        # Pipeline-specific configuration
        self.options = default_options
        self.enable_timing = self.options.get("enable_timing", True)
        self.enable_validation = self.options.get("enable_validation", True)
        self.max_retries = self.options.get("max_retries", 3)
        self.timeout = self.options.get("timeout", 120)
        self.retry_delay = self.options.get("retry_delay", 1.0)
        
        # QA-specific configuration
        self.qa_config = {
            "conversation_context": True,
            "response_enhancement": True,
            "xml_validation": True,
            "metadata_tracking": True
        }
        
        # Update QA config with any provided options
        if options:
            for key in ["conversation_context", "response_enhancement", "xml_validation", "metadata_tracking"]:
                if key in options:
                    self.qa_config[key] = options[key]
        
        # Performance tracking
        self._stage_timings: Dict[str, list] = {}
        self._execution_count = 0
        self._error_count = 0
        self._total_execution_time = 0.0
    
    def _on_initialize(self) -> None:
        """Custom initialization logic for QA pipeline."""
        self.logger.info(f"Initializing QAStrategyPipeline with options: {self.options}")
        
        # Initialize performance tracking
        if self.enable_timing:
            self.logger.info("Performance timing enabled")
        
        # Log strategy information
        self.logger.info(f"Prompt strategy: {self.prompt_strategy.get_strategy_info()['name']}")
        self.logger.info(f"Response strategy: {self.response_strategy.get_strategy_info()['name']}")
        self.logger.info(f"XML strategy: {self.xml_strategy.get_strategy_info()['name']}")
        self.logger.info(f"LLM client: {self.llm_client.get_client_info()['client_type']}")
        
        # Log QA-specific configuration
        self.logger.info(f"QA Configuration: {self.qa_config}")
        self.logger.info(f"Configuration: timing={self.enable_timing}, validation={self.enable_validation}")
        self.logger.info(f"Retry settings: max_retries={self.max_retries}, delay={self.retry_delay}s")
    
    def _on_shutdown(self) -> None:
        """Custom shutdown logic for QA pipeline."""
        self.logger.info("Shutting down QAStrategyPipeline")
        
        # Log execution statistics
        self.logger.info(f"Total QA executions: {self._execution_count}")
        self.logger.info(f"Total QA errors: {self._error_count}")
        
        if self._execution_count > 0:
            avg_time = self._total_execution_time / self._execution_count
            self.logger.info(f"Average QA execution time: {avg_time:.3f} seconds")
        
        if self.enable_timing and self._stage_timings:
            self.logger.info("QA Performance summary:")
            for stage, timings in self._stage_timings.items():
                if timings:
                    avg_time = sum(timings) / len(timings)
                    self.logger.info(f"  {stage}: {avg_time:.3f}s (avg of {len(timings)} executions)")
    
    def on_prompt_generated(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after prompt is generated."""
        self.logger.info("✓ QA prompt generation completed successfully")
    
    def on_response_received(self, raw_response: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after LLM response is received."""
        self.logger.info("✓ QA LLM response received successfully")
    
    def on_response_processed(self, structured_response: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after response is processed."""
        self.logger.info("✓ QA response processing completed successfully")
    
    def on_xml_generated(self, xml_element: Element, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after XML is generated."""
        self.logger.info("✓ QA XML generation completed successfully")
    
    def on_error(self, error: Exception, stage: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called when an error occurs during pipeline execution."""
        self._error_count += 1
        self.logger.error(f"✗ Error in QA {stage} stage: {str(error)}")
    
    def _record_stage_timing(self, stage: str, duration: float) -> None:
        """Record timing for a pipeline stage."""
        if stage not in self._stage_timings:
            self._stage_timings[stage] = []
        self._stage_timings[stage].append(duration)
        self.logger.debug(f"QA stage '{stage}' took {duration:.3f} seconds")
    
    def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """Execute QA pipeline with execution counting and enhanced logging."""
        execution_start = time.time()
        self._execution_count += 1
        self.logger.info(f"Starting QA pipeline execution #{self._execution_count}")
        
        try:
            result = super().execute(input_data, context, model, **kwargs)
            execution_time = time.time() - execution_start
            self._total_execution_time += execution_time
            self.logger.info(f"✓ QA pipeline execution #{self._execution_count} completed successfully in {execution_time:.3f}s")
            return result
        except Exception as e:
            self._error_count += 1
            execution_time = time.time() - execution_start
            self.logger.error(f"✗ QA pipeline execution #{self._execution_count} failed after {execution_time:.3f}s: {str(e)}")
            raise
    
    def _validate_input_data(self, input_data: Dict[str, Any]) -> None:
        """Validate input data for QA workflows.
        
        Args:
            input_data: Input data dictionary
            
        Raises:
            ValidationError: If input data is invalid
        """
        if not isinstance(input_data, dict):
            raise ValidationError("Input data must be a dictionary for QA pipeline")
        
        if not input_data:
            raise ValidationError("Input data cannot be empty for QA pipeline")
        
        # Check for required Q&A fields
        has_question = "question" in input_data and input_data["question"]
        has_user_input = "user_input" in input_data and input_data["user_input"]
        
        if not (has_question or has_user_input):
            raise ValidationError("QA pipeline requires either 'question' or 'user_input' field")
        
        # Validate question format if present
        if has_question and not isinstance(input_data["question"], str):
            raise ValidationError("Question must be a string")
        
        # Validate user_input format if present
        if has_user_input and not isinstance(input_data["user_input"], str):
            raise ValidationError("User input must be a string")
        
        # Validate conversation history if present
        if "conversation_history" in input_data:
            if not isinstance(input_data["conversation_history"], list):
                raise ValidationError("Conversation history must be a list")
            
            for msg in input_data["conversation_history"]:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    raise ValidationError("Each conversation message must have 'role' and 'content' fields")
    
    def _validate_structured_response(self, response: Dict[str, Any]) -> None:
        """Validate structured response for QA workflows.
        
        Args:
            response: Structured response dictionary
            
        Raises:
            ValidationError: If response is invalid
        """
        if not isinstance(response, dict):
            raise ValidationError("Structured response must be a dictionary for QA pipeline")
        
        if not response:
            raise ValidationError("Structured response cannot be empty for QA pipeline")
        
        # Check for required answer field
        if "answer" not in response:
            raise ValidationError("QA response must contain an 'answer' field")
        
        if not isinstance(response["answer"], str) or not response["answer"].strip():
            raise ValidationError("Answer must be a non-empty string")
        
        # Validate confidence if present
        if "confidence" in response:
            confidence = response["confidence"]
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
                raise ValidationError("Confidence must be a number between 0 and 1")
        
        # Validate sources if present
        if "sources" in response:
            sources = response["sources"]
            if not isinstance(sources, list):
                raise ValidationError("Sources must be a list")
            
            for source in sources:
                if not isinstance(source, dict) or "title" not in source:
                    raise ValidationError("Each source must be a dictionary with a 'title' field")
    
    def _execute_prompt_stage(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Execute the prompt generation stage with QA-specific validation.
        
        Args:
            input_data: Input data for prompt generation
            context: Optional context information
            
        Returns:
            Generated prompt string
            
        Raises:
            PipelineError: If prompt generation fails
        """
        start_time = time.time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing QA prompt generation stage...")
            
            # Validate input data
            self._validate_input_data(input_data)
            
            # Generate prompt using QA strategy
            prompt = self.prompt_strategy.create_prompt(input_data, context)
            
            if not prompt or not isinstance(prompt, str):
                raise PipelineError("QA prompt strategy returned invalid prompt")
            
            self.logger.info(f"Generated QA prompt length: {len(prompt)} characters")
            
            # Log QA-specific prompt details
            if self.qa_config.get("conversation_context", True):
                self.logger.debug(f"QA prompt includes conversation context: {'conversation_history' in input_data}")
                if "conversation_history" in input_data:
                    self.logger.debug(f"Conversation history length: {len(input_data['conversation_history'])} messages")
            
            # Record timing
            if start_time is not None:
                duration = time.time() - start_time
                self._record_stage_timing("prompt", duration)
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"QA prompt generation failed: {str(e)}")
            raise PipelineError(f"QA prompt generation failed: {str(e)}") from e
    
    def _execute_response_stage(self, raw_response: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the response processing stage with QA-specific validation.
        
        Args:
            raw_response: Raw response from LLM
            context: Optional context information
            
        Returns:
            Structured response dictionary
            
        Raises:
            PipelineError: If response processing fails
        """
        start_time = time.time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing QA response processing stage...")
            
            # Process response using QA strategy
            structured_response = self.response_strategy.process_response(raw_response, context)
            
            if not structured_response or not isinstance(structured_response, dict):
                raise PipelineError("QA response strategy returned invalid response")
            
            # Validate structured response
            self._validate_structured_response(structured_response)
            
            self.logger.info(f"Processed QA response with {len(structured_response)} top-level keys")
            
            # Log QA-specific response details
            if self.qa_config.get("response_enhancement", True):
                self.logger.debug(f"Answer length: {len(structured_response.get('answer', ''))}")
                self.logger.debug(f"Confidence: {structured_response.get('confidence', 'N/A')}")
                self.logger.debug(f"Sources count: {len(structured_response.get('sources', []))}")
                self.logger.debug(f"Follow-up questions count: {len(structured_response.get('follow_up_questions', []))}")
            
            # Record timing
            if start_time is not None:
                duration = time.time() - start_time
                self._record_stage_timing("response", duration)
            
            return structured_response
            
        except Exception as e:
            self.logger.error(f"QA response processing failed: {str(e)}")
            raise PipelineError(f"QA response processing failed: {str(e)}") from e
    
    def _execute_llm_stage(self, prompt: str, model: str, **kwargs) -> str:
        """Execute the LLM generation stage with QA-specific handling.
        
        Args:
            prompt: Generated prompt string
            model: Model to use
            **kwargs: Additional LLM parameters
            
        Returns:
            Raw response from LLM
            
        Raises:
            PipelineError: If LLM generation fails
        """
        start_time = time.time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing QA LLM generation stage...")
            
            # Generate response using LLM client
            raw_response = self.llm_client.generate_response(prompt, model=model, **kwargs)
            
            if not raw_response or not isinstance(raw_response, str):
                raise PipelineError("LLM client returned invalid response")
            
            self.logger.info(f"Generated QA response length: {len(raw_response)} characters")
            
            # Log QA-specific LLM details
            if self.qa_config.get("response_enhancement", True):
                self.logger.debug(f"Response preview: {raw_response[:100]}...")
                self.logger.debug(f"Response contains JSON: {'{' in raw_response and '}' in raw_response}")
            
            # Record timing
            if start_time is not None:
                duration = time.time() - start_time
                self._record_stage_timing("llm", duration)
            
            return raw_response
            
        except Exception as e:
            self.logger.error(f"QA LLM generation failed: {str(e)}")
            raise PipelineError(f"QA LLM generation failed: {str(e)}") from e
    
    def _execute_xml_stage(self, structured_response: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Element:
        """Execute the XML generation stage with QA-specific validation.
        
        Args:
            structured_response: Structured response data
            context: Optional context information
            
        Returns:
            XML element
            
        Raises:
            PipelineError: If XML generation fails
        """
        start_time = time.time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing QA XML generation stage...")
            
            # Generate XML using QA strategy
            xml_element = self.xml_strategy.transform_to_xml(structured_response, context)
            
            if xml_element is None:
                raise PipelineError("QA XML strategy returned None")
            
            # Validate XML if enabled
            if self.qa_config.get("xml_validation", True):
                is_valid = self.xml_strategy.validate_xml(xml_element)
                if not is_valid:
                    raise PipelineError("Generated XML failed validation against XSD schema")
                self.logger.debug("XML validation passed against XSD schema")
            
            self.logger.info(f"Generated QA XML element: {xml_element.tag} with {len(xml_element)} children")
            
            # Log QA-specific XML details
            if self.qa_config.get("metadata_tracking", True):
                self.logger.debug(f"XML namespace: {xml_element.tag.split('}')[0] if '}' in xml_element.tag else 'default'}")
                self.logger.debug(f"XML root element: {xml_element.tag}")
            
            # Record timing
            if start_time is not None:
                duration = time.time() - start_time
                self._record_stage_timing("xml", duration)
            
            return xml_element
            
        except Exception as e:
            self.logger.error(f"QA XML generation failed: {str(e)}")
            raise PipelineError(f"QA XML generation failed: {str(e)}") from e
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the QA pipeline.
        
        Returns:
            Dictionary with pipeline information
        """
        base_info = super().get_pipeline_info()
        
        # Add QA-specific information
        qa_info = {
            "pipeline_type": "QAStrategyPipeline",
            "qa_config": self.qa_config,
            "strategies": {
                "prompt": self.prompt_strategy.get_strategy_info() if hasattr(self.prompt_strategy, 'get_strategy_info') else {"name": "QAPromptStrategy"},
                "response": self.response_strategy.get_strategy_info() if hasattr(self.response_strategy, 'get_strategy_info') else {"name": "QAResponseStrategy"},
                "xml": self.xml_strategy.get_strategy_info() if hasattr(self.xml_strategy, 'get_strategy_info') else {"name": "QAXmlOutputStrategy"}
            },
            "features": {
                **base_info.get("features", {}),
                "conversation_context": self.qa_config.get("conversation_context", True),
                "response_enhancement": self.qa_config.get("response_enhancement", True),
                "xml_validation": self.qa_config.get("xml_validation", True),
                "metadata_tracking": self.qa_config.get("metadata_tracking", True)
            }
        }
        
        return qa_info
    
    def get_qa_metrics(self) -> Dict[str, Any]:
        """Get QA-specific metrics and statistics.
        
        Returns:
            Dictionary with QA metrics
        """
        return {
            "total_questions_processed": self._execution_count,
            "successful_qa_workflows": self._execution_count - self._error_count,
            "failed_qa_workflows": self._error_count,
            "qa_success_rate": (self._execution_count - self._error_count) / max(self._execution_count, 1),
            "average_qa_processing_time": sum(sum(timings) for timings in self._stage_timings.values()) / max(self._execution_count, 1) if self._stage_timings else 0,
            "qa_configuration": self.qa_config
        }
