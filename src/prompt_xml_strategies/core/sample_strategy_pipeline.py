"""Sample strategy pipeline implementation demonstrating the pipeline pattern."""

from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element
import logging

from .base_strategy_pipeline import BaseStrategyPipeline
from ..prompt_strategies.interface import PromptCreationStrategy
from ..response_strategies.interface import ResponseCreationStrategy
from ..xml_output_strategies.interface import XmlOutputStrategy
from ..llm_clients.base_client import BaseLLMClient
from .exceptions import PipelineError


class SampleStrategyPipeline(BaseStrategyPipeline):
    """Sample implementation of the strategy pipeline pattern.
    
    This class demonstrates how to extend BaseStrategyPipeline to create
    a concrete pipeline implementation with custom behavior, logging,
    and lifecycle management.
    
    Features:
    - Enhanced logging at each stage
    - Performance timing
    - Custom validation
    - Error recovery mechanisms
    - Configurable behavior through options
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
        
        # Timing and metrics
        self._stage_timings = {}
        self._execution_count = 0
        self._error_count = 0
    
    def _on_initialize(self) -> None:
        """Custom initialization logic for sample pipeline."""
        self.logger.info(f"Initializing SampleStrategyPipeline with options: {self.options}")
        
        # Initialize performance tracking
        if self.enable_timing:
            import time
            self._start_time = time.time()
            self.logger.info("Performance timing enabled")
        
        # Log strategy information
        self.logger.info(f"Prompt strategy: {self.prompt_strategy.get_strategy_info()['name']}")
        self.logger.info(f"Response strategy: {self.response_strategy.get_strategy_info()['name']}")
        self.logger.info(f"XML strategy: {self.xml_strategy.get_strategy_info()['name']}")
        self.logger.info(f"LLM client: {self.llm_client.get_client_info()['client_type']}")
    
    def _on_shutdown(self) -> None:
        """Custom shutdown logic for sample pipeline."""
        self.logger.info("Shutting down SampleStrategyPipeline")
        
        # Log execution statistics
        self.logger.info(f"Total executions: {self._execution_count}")
        self.logger.info(f"Total errors: {self._error_count}")
        
        if self.enable_timing and self._stage_timings:
            self.logger.info("Performance summary:")
            for stage, timings in self._stage_timings.items():
                avg_time = sum(timings) / len(timings)
                self.logger.info(f"  {stage}: avg {avg_time:.3f}s ({len(timings)} executions)")
    
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
        start_time = self._get_current_time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing prompt generation stage...")
            
            # Optional input validation
            if self.enable_validation:
                self._validate_input_data(input_data)
            
            # Generate prompt using strategy
            prompt = self.prompt_strategy.create_prompt(input_data, context)
            
            # Log prompt details
            self.logger.info(f"Generated prompt length: {len(prompt)} characters")
            self.logger.debug(f"Generated prompt: {prompt[:100]}..." if len(prompt) > 100 else prompt)
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"Prompt generation failed: {str(e)}")
            raise PipelineError(f"Prompt generation failed: {str(e)}") from e
        finally:
            if start_time and self.enable_timing:
                self._record_stage_timing("prompt", self._get_current_time() - start_time)
    
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
        start_time = self._get_current_time() if self.enable_timing else None
        
        try:
            self.logger.info(f"Executing LLM stage with model: {model}")
            
            # Retry logic for LLM requests
            last_exception = None
            for attempt in range(self.max_retries):
                try:
                    if attempt > 0:
                        self.logger.warning(f"LLM request attempt {attempt + 1}/{self.max_retries}")
                    
                    raw_response = self.llm_client.generate_response(prompt, model=model, **kwargs)
                    
                    # Log response details
                    self.logger.info(f"Received LLM response length: {len(raw_response)} characters")
                    self.logger.debug(f"LLM response: {raw_response[:200]}..." if len(raw_response) > 200 else raw_response)
                    
                    return raw_response
                    
                except Exception as e:
                    last_exception = e
                    self.logger.warning(f"LLM request attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            # All retries failed
            raise PipelineError(f"LLM request failed after {self.max_retries} attempts: {str(last_exception)}")
            
        finally:
            if start_time and self.enable_timing:
                self._record_stage_timing("llm", self._get_current_time() - start_time)
    
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
        start_time = self._get_current_time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing response processing stage...")
            
            # Process response using strategy
            structured_response = self.response_strategy.process_response(raw_response, context)
            
            # Optional response validation
            if self.enable_validation:
                self._validate_structured_response(structured_response)
            
            # Log response details
            self.logger.info(f"Processed response with {len(structured_response)} top-level keys")
            self.logger.debug(f"Response keys: {list(structured_response.keys())}")
            
            return structured_response
            
        except Exception as e:
            self.logger.error(f"Response processing failed: {str(e)}")
            raise PipelineError(f"Response processing failed: {str(e)}") from e
        finally:
            if start_time and self.enable_timing:
                self._record_stage_timing("response", self._get_current_time() - start_time)
    
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
        start_time = self._get_current_time() if self.enable_timing else None
        
        try:
            self.logger.info("Executing XML generation stage...")
            
            # Generate XML using strategy
            xml_element = self.xml_strategy.transform_to_xml(structured_response, context)
            
            # Optional XML validation
            if self.enable_validation:
                self._validate_xml_element(xml_element)
            
            # Log XML details
            self.logger.info(f"Generated XML element: <{xml_element.tag}> with {len(xml_element)} children")
            
            return xml_element
            
        except Exception as e:
            self.logger.error(f"XML generation failed: {str(e)}")
            raise PipelineError(f"XML generation failed: {str(e)}") from e
        finally:
            if start_time and self.enable_timing:
                self._record_stage_timing("xml", self._get_current_time() - start_time)
    
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
        self._error_count += 1
        self.logger.error(f"✗ Error in {stage} stage: {str(error)}")
    
    def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """Execute pipeline with execution counting and enhanced logging."""
        self._execution_count += 1
        self.logger.info(f"Starting pipeline execution #{self._execution_count}")
        
        try:
            result = super().execute(input_data, context, model, **kwargs)
            self.logger.info(f"✓ Pipeline execution #{self._execution_count} completed successfully")
            return result
        except Exception as e:
            self._error_count += 1
            self.logger.error(f"✗ Pipeline execution #{self._execution_count} failed: {str(e)}")
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
            "stage_timings": self._stage_timings if self.enable_timing else None,
            "features": {
                "timing": self.enable_timing,
                "validation": self.enable_validation,
                "retries": self.max_retries > 1,
                "timeout": self.timeout
            }
        })
        
        return base_info
    
    # Private helper methods
    
    def _get_current_time(self) -> float:
        """Get current time for performance measurement."""
        import time
        return time.time()
    
    def _record_stage_timing(self, stage: str, duration: float) -> None:
        """Record timing for a pipeline stage."""
        if stage not in self._stage_timings:
            self._stage_timings[stage] = []
        self._stage_timings[stage].append(duration)
        self.logger.debug(f"Stage '{stage}' took {duration:.3f} seconds")
    
    def _validate_input_data(self, input_data: Dict[str, Any]) -> None:
        """Validate input data structure."""
        if not isinstance(input_data, dict):
            raise ValueError("Input data must be a dictionary")
        if not input_data:
            raise ValueError("Input data cannot be empty")
    
    def _validate_structured_response(self, structured_response: Dict[str, Any]) -> None:
        """Validate structured response data."""
        if not isinstance(structured_response, dict):
            raise ValueError("Structured response must be a dictionary")
        if not structured_response:
            raise ValueError("Structured response cannot be empty")
    
    def _validate_xml_element(self, xml_element: Element) -> None:
        """Validate XML element."""
        if xml_element is None:
            raise ValueError("XML element cannot be None")
        if not xml_element.tag:
            raise ValueError("XML element must have a valid tag")