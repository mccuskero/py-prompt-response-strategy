"""Pipeline for orchestrating the three-tier strategy system."""

from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element, tostring
import logging

from .base_strategy_pipeline import BaseStrategyPipeline
from ..prompt_strategies.interface import PromptCreationStrategy
from ..response_strategies.interface import ResponseCreationStrategy
from ..xml_output_strategies.interface import XmlOutputStrategy
from ..llm_clients.base_client import BaseLLMClient
from .exceptions import PipelineError, ValidationError


class TripleStrategyPipeline(BaseStrategyPipeline):
    """Pipeline that orchestrates prompt creation, response processing, and XML output.
    
    This is a simple implementation of the BaseStrategyPipeline that provides
    straightforward execution of the three-tier strategy system without
    additional features like timing, retries, or extensive logging.
    """
    
    def __init__(
        self,
        prompt_strategy: PromptCreationStrategy,
        response_strategy: ResponseCreationStrategy,
        xml_strategy: XmlOutputStrategy,
        llm_client: BaseLLMClient,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the pipeline with three strategies and an LLM client.
        
        Args:
            prompt_strategy: Strategy for creating prompts
            response_strategy: Strategy for processing responses
            xml_strategy: Strategy for XML output
            llm_client: LLM client for generating responses
            logger: Optional logger for pipeline operations
        """
        super().__init__(prompt_strategy, response_strategy, xml_strategy, llm_client, logger)

    def _execute_prompt_stage(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> str:
        """Execute the prompt generation stage.

        Args:
            input_data: Input data for prompt generation
            context: Optional context information

        Returns:
            Generated prompt string
        """
        return self.prompt_strategy.create_prompt(input_data, context)

    def _execute_llm_stage(self, prompt: str, model: str, **kwargs) -> str:
        """Execute the LLM response stage.

        Args:
            prompt: Generated prompt
            model: LLM model to use
            **kwargs: Additional LLM parameters

        Returns:
            Raw LLM response
        """
        return self.llm_client.generate_response(prompt, model=model, **kwargs)

    def _execute_response_stage(self, raw_response: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the response processing stage.

        Args:
            raw_response: Raw LLM response
            context: Optional context information

        Returns:
            Structured response data
        """
        return self.response_strategy.process_response(raw_response, context)

    def _execute_xml_stage(self, structured_response: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Element:
        """Execute the XML generation stage.

        Args:
            structured_response: Processed response data
            context: Optional context information

        Returns:
            XML Element
        """
        return self.xml_strategy.transform_to_xml(structured_response, context)
    
    def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        model: str = "default",
        **llm_kwargs
    ) -> Dict[str, Any]:
        """Execute the complete pipeline.
        
        Args:
            input_data: Input data for prompt generation
            context: Optional context information
            model: LLM model to use
            **llm_kwargs: Additional LLM parameters
            
        Returns:
            Dictionary containing all pipeline results
            
        Raises:
            PipelineError: If any stage of the pipeline fails
        """
        try:
            # Stage 1: Create prompt
            prompt = self._execute_prompt_stage(input_data, context)

            # Stage 2: Generate LLM response
            raw_response = self._execute_llm_stage(prompt, model, **llm_kwargs)

            # Stage 3: Process response
            structured_response = self._execute_response_stage(raw_response, context)

            # Stage 4: Transform to XML
            xml_element = self._execute_xml_stage(structured_response, context)
            
            # Return all results
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
            
        except Exception as e:
            raise PipelineError(f"Pipeline execution failed: {str(e)}") from e
    
    def validate_pipeline(self) -> bool:
        """Validate that all strategies and client are properly configured.
        
        Returns:
            True if pipeline is valid
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate strategies exist
        if not self.prompt_strategy:
            raise ValidationError("Prompt strategy is required")
        
        if not self.response_strategy:
            raise ValidationError("Response strategy is required")
        
        if not self.xml_strategy:
            raise ValidationError("XML strategy is required")
        
        if not self.llm_client:
            raise ValidationError("LLM client is required")
        
        # Validate LLM client connection
        try:
            self.llm_client.validate_connection()
        except Exception as e:
            raise ValidationError(f"LLM client validation failed: {str(e)}")
        
        return True
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline configuration.
        
        Returns:
            Dictionary with pipeline metadata
        """
        return {
            "prompt_strategy": self.prompt_strategy.get_strategy_info(),
            "response_strategy": self.response_strategy.get_strategy_info(),
            "xml_strategy": self.xml_strategy.get_strategy_info(),
            "llm_client": self.llm_client.get_client_info(),
            "pipeline_type": "TripleStrategyPipeline",
            "version": "1.0.0"
        }
    
    def create_prompt_only(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute only the prompt creation stage.
        
        Args:
            input_data: Input data for prompt generation
            context: Optional context information
            
        Returns:
            Generated prompt string
        """
        return self.prompt_strategy.create_prompt(input_data, context)
    
    def process_response_only(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute only the response processing stage.
        
        Args:
            raw_response: Raw response to process
            context: Optional context information
            
        Returns:
            Structured response data
        """
        return self.response_strategy.process_response(raw_response, context)
    
    def create_xml_only(
        self,
        response_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Element:
        """Execute only the XML creation stage.
        
        Args:
            response_data: Structured response data
            context: Optional context information
            
        Returns:
            XML Element
        """
        return self.xml_strategy.transform_to_xml(response_data, context)