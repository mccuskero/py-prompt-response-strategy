"""Interface for strategy pipeline implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element

from ..prompt_strategies.interface import PromptCreationStrategy
from ..response_strategies.interface import ResponseCreationStrategy
from ..xml_output_strategies.interface import XmlOutputStrategy
from ..llm_clients.base_client import BaseLLMClient


class StrategyPipelineInterface(ABC):
    """Abstract interface for strategy pipeline implementations.
    
    This interface defines the contract for pipeline implementations that
    coordinate prompt creation, response processing, and XML output strategies
    along with LLM client integration.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the pipeline and all its components.
        
        This method should prepare all strategies and clients for execution.
        It may include validation, connection testing, or resource allocation.
        
        Raises:
            PipelineError: If initialization fails
        """
        pass
    
    @abstractmethod
    def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the complete pipeline with all three strategy tiers.
        
        Args:
            input_data: Input data for prompt generation
            context: Optional context information
            model: LLM model to use
            **kwargs: Additional parameters for LLM or strategies
            
        Returns:
            Dictionary containing all pipeline results including:
            - input_data: Original input data
            - context: Context used
            - prompt: Generated prompt
            - raw_response: Raw LLM response
            - structured_response: Processed response
            - xml_element: Generated XML element
            - xml_string: XML as string
            - pipeline_info: Pipeline metadata
            
        Raises:
            PipelineError: If pipeline execution fails
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the pipeline and cleanup resources.
        
        This method should properly close connections, release resources,
        and perform any necessary cleanup operations.
        """
        pass
    
    @abstractmethod
    def validate_pipeline(self) -> bool:
        """Validate that all pipeline components are properly configured.
        
        Returns:
            True if pipeline is valid and ready for execution
            
        Raises:
            ValidationError: If pipeline validation fails
        """
        pass
    
    @abstractmethod
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the pipeline configuration.
        
        Returns:
            Dictionary with pipeline metadata including strategy info,
            client info, and pipeline-specific configuration
        """
        pass
    
    # Optional lifecycle methods that implementations can override
    def on_prompt_generated(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after prompt is generated.
        
        Args:
            prompt: The generated prompt
            context: Context used for generation
        """
        pass
    
    def on_response_received(self, raw_response: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after LLM response is received.
        
        Args:
            raw_response: Raw response from LLM
            context: Context used for processing
        """
        pass
    
    def on_response_processed(self, structured_response: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after response is processed.
        
        Args:
            structured_response: Processed response data
            context: Context used for processing
        """
        pass
    
    def on_xml_generated(self, xml_element: Element, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called after XML is generated.
        
        Args:
            xml_element: Generated XML element
            context: Context used for generation
        """
        pass
    
    def on_error(self, error: Exception, stage: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Hook called when an error occurs during pipeline execution.
        
        Args:
            error: The exception that occurred
            stage: Pipeline stage where error occurred ('prompt', 'llm', 'response', 'xml')
            context: Context at time of error
        """
        pass