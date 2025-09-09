"""Abstract base class for strategy pipeline implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element, tostring
import logging

from .strategy_pipeline_interface import StrategyPipelineInterface
from ..prompt_strategies.interface import PromptCreationStrategy
from ..response_strategies.interface import ResponseCreationStrategy
from ..xml_output_strategies.interface import XmlOutputStrategy
from ..llm_clients.base_client import BaseLLMClient
from .exceptions import ValidationError, PipelineError


class BaseStrategyPipeline(StrategyPipelineInterface, ABC):
    """Abstract base class providing common pipeline functionality.
    
    This class provides a template method pattern implementation of the
    StrategyPipelineInterface with common functionality for initialization,
    validation, and execution flow.
    
    Subclasses must implement the abstract methods to define specific
    pipeline behavior while inheriting common pipeline management features.
    """
    
    def __init__(
        self,
        prompt_strategy: PromptCreationStrategy,
        response_strategy: ResponseCreationStrategy,
        xml_strategy: XmlOutputStrategy,
        llm_client: BaseLLMClient,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the base pipeline with required strategies and client.
        
        Args:
            prompt_strategy: Strategy for creating prompts
            response_strategy: Strategy for processing responses
            xml_strategy: Strategy for XML output
            llm_client: LLM client for generating responses
            logger: Optional logger for pipeline operations
        """
        self.prompt_strategy = prompt_strategy
        self.response_strategy = response_strategy
        self.xml_strategy = xml_strategy
        self.llm_client = llm_client
        
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
        self._initialized = False
        self._shutdown = False
        
        # Lifecycle state tracking
        self._current_stage = None
        self._execution_context = None
    
    def initialize(self) -> None:
        """Initialize the pipeline and all its components.
        
        This default implementation performs basic validation and setup.
        Subclasses can override to add specific initialization logic.
        
        Raises:
            PipelineError: If initialization fails
        """
        try:
            self.logger.info("Initializing pipeline...")
            
            # Validate all components are present
            self.validate_pipeline()
            
            # Perform component-specific initialization
            self._initialize_strategies()
            self._initialize_client()
            
            # Custom initialization hook
            self._on_initialize()
            
            self._initialized = True
            self.logger.info("Pipeline initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Pipeline initialization failed: {str(e)}")
            raise PipelineError(f"Pipeline initialization failed: {str(e)}") from e
    
    def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the complete pipeline with error handling and lifecycle hooks.
        
        This template method implements the standard pipeline execution flow
        with proper error handling, logging, and lifecycle hook calls.
        
        Args:
            input_data: Input data for prompt generation
            context: Optional context information
            model: LLM model to use
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing all pipeline results
            
        Raises:
            PipelineError: If pipeline execution fails
        """
        if not self._initialized:
            raise PipelineError("Pipeline must be initialized before execution")
        
        if self._shutdown:
            raise PipelineError("Pipeline has been shutdown")
        
        self._execution_context = {
            "input_data": input_data,
            "context": context,
            "model": model,
            "kwargs": kwargs
        }
        
        try:
            self.logger.info("Starting pipeline execution...")
            
            # Stage 1: Prompt Generation
            self._current_stage = "prompt"
            prompt = self._execute_prompt_stage(input_data, context)
            self.on_prompt_generated(prompt, context)
            
            # Stage 2: LLM Response
            self._current_stage = "llm"
            raw_response = self._execute_llm_stage(prompt, model, **kwargs)
            self.on_response_received(raw_response, context)
            
            # Stage 3: Response Processing
            self._current_stage = "response"
            structured_response = self._execute_response_stage(raw_response, context)
            self.on_response_processed(structured_response, context)
            
            # Stage 4: XML Generation
            self._current_stage = "xml"
            xml_element = self._execute_xml_stage(structured_response, context)
            self.on_xml_generated(xml_element, context)
            
            # Build final result
            result = self._build_result(
                input_data, context, prompt, raw_response, 
                structured_response, xml_element
            )
            
            self.logger.info("Pipeline execution completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed at stage '{self._current_stage}': {str(e)}")
            self.on_error(e, self._current_stage or "unknown", context)
            raise PipelineError(f"Pipeline execution failed at stage '{self._current_stage}': {str(e)}") from e
        finally:
            self._current_stage = None
            self._execution_context = None
    
    def shutdown(self) -> None:
        """Shutdown the pipeline and cleanup resources.
        
        This default implementation performs basic cleanup.
        Subclasses can override to add specific shutdown logic.
        """
        try:
            self.logger.info("Shutting down pipeline...")
            
            # Custom shutdown hook
            self._on_shutdown()
            
            # Mark as shutdown
            self._shutdown = True
            self._initialized = False
            
            self.logger.info("Pipeline shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Pipeline shutdown failed: {str(e)}")
            raise PipelineError(f"Pipeline shutdown failed: {str(e)}") from e
    
    def validate_pipeline(self) -> bool:
        """Validate that all pipeline components are properly configured.
        
        Returns:
            True if pipeline is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not self.prompt_strategy:
            raise ValidationError("Prompt strategy is required")
        
        if not self.response_strategy:
            raise ValidationError("Response strategy is required")
        
        if not self.xml_strategy:
            raise ValidationError("XML strategy is required")
        
        if not self.llm_client:
            raise ValidationError("LLM client is required")
        
        # Validate LLM client connection if not shutdown
        if not self._shutdown:
            try:
                self.llm_client.validate_connection()
            except Exception as e:
                raise ValidationError(f"LLM client validation failed: {str(e)}")
        
        return True
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the pipeline configuration.
        
        Returns:
            Dictionary with pipeline metadata
        """
        return {
            "pipeline_type": self.__class__.__name__,
            "initialized": self._initialized,
            "shutdown": self._shutdown,
            "current_stage": self._current_stage,
            "prompt_strategy": self.prompt_strategy.get_strategy_info(),
            "response_strategy": self.response_strategy.get_strategy_info(),
            "xml_strategy": self.xml_strategy.get_strategy_info(),
            "llm_client": self.llm_client.get_client_info(),
            "version": "1.0.0"
        }
    
    # Template method hooks for subclasses
    
    def _on_initialize(self) -> None:
        """Hook called during initialization. Override in subclasses."""
        pass
    
    def _on_shutdown(self) -> None:
        """Hook called during shutdown. Override in subclasses."""
        pass
    
    def _initialize_strategies(self) -> None:
        """Initialize strategies. Override in subclasses for custom logic."""
        # Default implementation - strategies are assumed to be ready
        pass
    
    def _initialize_client(self) -> None:
        """Initialize LLM client. Override in subclasses for custom logic."""
        # Default implementation - validate connection
        self.llm_client.validate_connection()
    
    # Abstract methods for pipeline stages - must be implemented by subclasses
    
    @abstractmethod
    def _execute_prompt_stage(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        """Execute the prompt generation stage.
        
        Args:
            input_data: Input data for prompt generation
            context: Optional context information
            
        Returns:
            Generated prompt string
        """
        pass
    
    @abstractmethod
    def _execute_llm_stage(self, prompt: str, model: str, **kwargs) -> str:
        """Execute the LLM response stage.
        
        Args:
            prompt: Generated prompt
            model: Model to use
            **kwargs: Additional LLM parameters
            
        Returns:
            Raw LLM response
        """
        pass
    
    @abstractmethod
    def _execute_response_stage(self, raw_response: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the response processing stage.
        
        Args:
            raw_response: Raw LLM response
            context: Optional context information
            
        Returns:
            Structured response data
        """
        pass
    
    @abstractmethod
    def _execute_xml_stage(self, structured_response: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Element:
        """Execute the XML generation stage.
        
        Args:
            structured_response: Processed response data
            context: Optional context information
            
        Returns:
            Generated XML element
        """
        pass
    
    def _build_result(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        prompt: str,
        raw_response: str,
        structured_response: Dict[str, Any],
        xml_element: Element
    ) -> Dict[str, Any]:
        """Build the final pipeline result dictionary.
        
        Subclasses can override to customize result format.
        
        Args:
            input_data: Original input data
            context: Context used
            prompt: Generated prompt
            raw_response: Raw LLM response
            structured_response: Processed response
            xml_element: Generated XML element
            
        Returns:
            Complete pipeline result dictionary
        """
        return {
            "input_data": input_data,
            "context": context,
            "prompt": prompt,
            "raw_response": raw_response,
            "structured_response": structured_response,
            "xml_element": xml_element,
            "xml_string": tostring(xml_element, encoding='unicode'),
            "pipeline_info": self.get_pipeline_info()
        }