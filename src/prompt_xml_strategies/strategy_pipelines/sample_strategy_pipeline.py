"""Sample strategy pipeline implementation demonstrating the pipeline pattern."""

from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element
import logging
import time

from ..core.strategy_pipeline import AbstractStrategyPipeline
from ..prompt_strategies.interface import PromptCreationStrategy
from ..response_strategies.interface import ResponseCreationStrategy
from ..xml_output_strategies.interface import XmlOutputStrategy
from ..llm_clients.base_client import BaseLLMClient
from ..core.exceptions import PipelineError, ValidationError


class SampleStrategyPipeline(AbstractStrategyPipeline):
    """Sample implementation of the strategy pipeline pattern.
    
    This class demonstrates how to extend AbstractStrategyPipeline to create
    a concrete pipeline implementation with custom behavior, logging,
    and lifecycle management.
    
    Features:
    - Enhanced logging at each stage
    - Performance timing and metrics
    - Custom validation and error handling
    - Retry mechanisms for LLM requests
    - Configurable behavior through options
    - Comprehensive lifecycle management
    """
    
    def __init__(
        self,
        prompt_strategy: PromptCreationStrategy,
        response_strategy: ResponseCreationStrategy,
        xml_strategy: XmlOutputStrategy,
        llm_client: BaseLLMClient,
        options: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the sample pipeline with optional configuration.
        
        Args:
            prompt_strategy: Strategy for creating prompts
            response_strategy: Strategy for processing responses
            xml_strategy: Strategy for XML output
            llm_client: LLM client for generating responses
            options: Optional configuration dictionary
            logger: Optional logger for pipeline operations
        """
        super().__init__(prompt_strategy, response_strategy, xml_strategy, llm_client, logger)
        
        # Pipeline-specific configuration
        self.options = options or {}
        self.enable_timing = self.options.get("enable_timing", False)
        self.enable_validation = self.options.get("enable_validation", True)
        self.max_retries = self.options.get("max_retries", 3)
        self.timeout = self.options.get("timeout", 120)  # seconds
        self.retry_delay = self.options.get("retry_delay", 1.0)  # seconds
        
        # Performance tracking
        self._stage_timings: Dict[str, list] = {}
        self._execution_count = 0
        self._error_count = 0
        self._total_execution_time = 0.0
    
    def _on_initialize(self) -> None:
        """Custom initialization logic for sample pipeline."""
        self.logger.info(f"Initializing SampleStrategyPipeline with options: {self.options}")
        
        # Initialize performance tracking
        if self.enable_timing:
            self.logger.info("Performance timing enabled")
        
        # Log strategy information
        self.logger.info(f"Prompt strategy: {self.prompt_strategy.get_strategy_info()['name']}")
        self.logger.info(f"Response strategy: {self.response_strategy.get_strategy_info()['name']}")
        self.logger.info(f"XML strategy: {self.xml_strategy.get_strategy_info()['name']}")
        self.logger.info(f"LLM client: {self.llm_client.get_client_info()['client_type']}")
        
        # Log configuration
        self.logger.info(f"Configuration: timing={self.enable_timing}, validation={self.enable_validation}")
        self.logger.info(f"Retry settings: max_retries={self.max_retries}, delay={self.retry_delay}s")
    
    def _on_shutdown(self) -> None:
        """Custom shutdown logic for sample pipeline."""
        self.logger.info("Shutting down SampleStrategyPipeline")
        
        # Log execution statistics
        self.logger.info(f"Total executions: {self._execution_count}")
        self.logger.info(f"Total errors: {self._error_count}")
        
        if self._execution_count > 0:
            avg_time = self._total_execution_time / self._execution_count
            self.logger.info(f"Average execution time: {avg_time:.3f} seconds")
        
        if self.enable_timing and self._stage_timings:
            self.logger.info("Performance summary:")
            for stage, timings in self._stage_timings.items():
                if timings:
                    avg_time = sum(timings) / len(timings)
                    min_time = min(timings)
                    max_time = max(timings)
                    self.logger.info(f"  {stage}: avg {avg_time:.3f}s, min {min_time:.3f}s, max {max_time:.3f}s ({len(timings)} executions)")
    
    def _execute_prompt_stage(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        """Execute the prompt generation stage with enhanced logging and validation.
        
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
            self.logger.info("Executing prompt generation stage...")
            
            # Optional input validation
            if self.enable_validation:
                self._validate_input_data(input_data)
            
            # Generate prompt using strategy
            prompt = self.prompt_strategy.create_prompt(input_data, context)
            
            # Log prompt details
            self.logger.info(f"Generated prompt length: {len(prompt)} characters")
            if self.logger.isEnabledFor(logging.DEBUG):
                preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
                self.logger.debug(f"Generated prompt: {preview}")
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"Prompt generation failed: {str(e)}")
            raise PipelineError(f"Prompt generation failed: {str(e)}") from e
        finally:
            if start_time and self.enable_timing:
                duration = time.time() - start_time
                self._record_stage_timing("prompt", duration)
    
    def _execute_llm_stage(self, prompt: str, model: str, **kwargs) -> str:
        """Execute the LLM response stage with retry logic.
        
        Args:
            prompt: Generated prompt
            model: Model to use
            **kwargs: Additional LLM parameters
            
        Returns:
            Raw LLM response
            
        Raises:
            PipelineError: If LLM request fails after retries
        """
        start_time = time.time() if self.enable_timing else None
        
        try:
            self.logger.info(f"Executing LLM stage with model: {model}")
            
            # Retry logic for LLM requests
            last_exception = None
            for attempt in range(self.max_retries):
                try:
                    if attempt > 0:
                        self.logger.warning(f"LLM request attempt {attempt + 1}/{self.max_retries}")
                        time.sleep(self.retry_delay * (2 ** (attempt - 1)))  # Exponential backoff
                    
                    raw_response = self.llm_client.generate_response(prompt, model=model, **kwargs)
                    
                    # Log response details
                    self.logger.info(f"Received LLM response length: {len(raw_response)} characters")
                    if self.logger.isEnabledFor(logging.DEBUG):
                        preview = raw_response[:200] + "..." if len(raw_response) > 200 else raw_response
                        self.logger.debug(f"LLM response: {preview}")
                    
                    return raw_response
                    
                except Exception as e:
                    last_exception = e
                    self.logger.warning(f"LLM request attempt {attempt + 1} failed: {str(e)}")
            
            # All retries failed
            raise PipelineError(f"LLM request failed after {self.max_retries} attempts: {str(last_exception)}")
            
        finally:
            if start_time and self.enable_timing:
                duration = time.time() - start_time
                self._record_stage_timing("llm", duration)
    
    def _execute_response_stage(self, raw_response: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the response processing stage with validation.
        
        Args:
            raw_response: Raw LLM response
            context: Optional context information
            
        Returns:
            Structured response data
            
        Raises:
            PipelineError: If response processing fails
        """
        start_time = time.time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing response processing stage...")
            
            # Process response using strategy
            structured_response = self.response_strategy.process_response(raw_response, context)
            
            # Optional response validation
            if self.enable_validation:
                self._validate_structured_response(structured_response)
            
            # Log response details
            self.logger.info(f"Processed response with {len(structured_response)} top-level keys")
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Response keys: {list(structured_response.keys())}")
            
            return structured_response
            
        except Exception as e:
            self.logger.error(f"Response processing failed: {str(e)}")
            raise PipelineError(f"Response processing failed: {str(e)}") from e
        finally:
            if start_time and self.enable_timing:
                duration = time.time() - start_time
                self._record_stage_timing("response", duration)
    
    def _execute_xml_stage(self, structured_response: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Element:
        """Execute the XML generation stage with validation.
        
        Args:
            structured_response: Processed response data
            context: Optional context information
            
        Returns:
            Generated XML element
            
        Raises:
            PipelineError: If XML generation fails
        """
        start_time = time.time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing XML generation stage...")
            
            # Generate XML using strategy
            xml_element = self.xml_strategy.transform_to_xml(structured_response, context)
            
            # Optional XML validation
            if self.enable_validation:
                self._validate_xml_element(xml_element)
            
            # Log XML details
            child_count = len(xml_element)
            self.logger.info(f"Generated XML element: <{xml_element.tag}> with {child_count} children")
            
            return xml_element
            
        except Exception as e:
            self.logger.error(f"XML generation failed: {str(e)}")
            raise PipelineError(f"XML generation failed: {str(e)}") from e
        finally:
            if start_time and self.enable_timing:
                duration = time.time() - start_time
                self._record_stage_timing("xml", duration)
    
    # Lifecycle hook implementations
    
    def on_prompt_generated(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after prompt is generated."""
        self.logger.info("✓ Prompt generation completed successfully")
    
    def on_response_received(self, raw_response: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after LLM response is received."""
        self.logger.info("✓ LLM response received successfully")
    
    def on_response_processed(self, structured_response: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after response is processed."""
        self.logger.info("✓ Response processing completed successfully")
    
    def on_xml_generated(self, xml_element: Element, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after XML is generated."""
        self.logger.info("✓ XML generation completed successfully")
    
    def on_error(self, error: Exception, stage: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called when an error occurs during pipeline execution."""
        # Don't double-count errors - they're already counted in the execute method
        self.logger.error(f"✗ Error in {stage} stage: {str(error)}")
    
    def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """Execute pipeline with execution counting and enhanced logging."""
        execution_start = time.time()
        self._execution_count += 1
        self.logger.info(f"Starting pipeline execution #{self._execution_count}")
        
        try:
            result = super().execute(input_data, context, model, **kwargs)
            execution_time = time.time() - execution_start
            self._total_execution_time += execution_time
            self.logger.info(f"✓ Pipeline execution #{self._execution_count} completed successfully in {execution_time:.3f}s")
            return result
        except Exception as e:
            self._error_count += 1
            execution_time = time.time() - execution_start
            self.logger.error(f"✗ Pipeline execution #{self._execution_count} failed after {execution_time:.3f}s: {str(e)}")
            raise
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get comprehensive information including sample pipeline metrics."""
        base_info = super().get_pipeline_info()
        
        # Add sample pipeline specific information
        base_info.update({
            "pipeline_type": "SampleStrategyPipeline",
            "options": self.options,
            "execution_count": self._execution_count,
            "error_count": self._error_count,
            "success_rate": (self._execution_count - self._error_count) / self._execution_count if self._execution_count > 0 else 1.0,
            "average_execution_time": self._total_execution_time / max(self._execution_count, 1),
            "stage_timings": self._stage_timings if self.enable_timing else None,
            "features": {
                "timing": self.enable_timing,
                "validation": self.enable_validation,
                "retries": self.max_retries > 1,
                "timeout": self.timeout,
                "retry_delay": self.retry_delay
            }
        })
        
        return base_info
    
    # Private helper methods
    
    def _record_stage_timing(self, stage: str, duration: float) -> None:
        """Record timing for a pipeline stage."""
        if stage not in self._stage_timings:
            self._stage_timings[stage] = []
        self._stage_timings[stage].append(duration)
        self.logger.debug(f"Stage '{stage}' took {duration:.3f} seconds")
    
    def _validate_input_data(self, input_data: Dict[str, Any]) -> None:
        """Validate input data structure."""
        if not isinstance(input_data, dict):
            raise ValidationError("Input data must be a dictionary")
        if not input_data:
            raise ValidationError("Input data cannot be empty")
        
        # Additional validation can be added here
        self.logger.debug("Input data validation passed")
    
    def _validate_structured_response(self, structured_response: Dict[str, Any]) -> None:
        """Validate structured response data."""
        if not isinstance(structured_response, dict):
            raise ValidationError("Structured response must be a dictionary")
        if not structured_response:
            raise ValidationError("Structured response cannot be empty")
        
        # Additional validation can be added here
        self.logger.debug("Structured response validation passed")
    
    def _validate_xml_element(self, xml_element: Element) -> None:
        """Validate XML element."""
        if xml_element is None:
            raise ValidationError("XML element cannot be None")
        if not xml_element.tag:
            raise ValidationError("XML element must have a valid tag")
        
        # Additional XML validation can be added here
        self.logger.debug("XML element validation passed")