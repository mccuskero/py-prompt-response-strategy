#!/usr/bin/env python3
"""
Mock Demo application showcasing SampleStrategyPipeline functionality.

This application demonstrates how to use the SampleStrategyPipeline
with a mock LLM client, making it easy to run without external dependencies.
"""

import sys
import os
import logging
from typing import Dict, Any
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prompt_xml_strategies.strategy_pipelines import SampleStrategyPipeline
from prompt_xml_strategies.prompt_strategies.simple_prompt_strategy import SimplePromptCreationStrategy
from prompt_xml_strategies.response_strategies.simple_response_strategy import SimpleResponseCreationStrategy
from prompt_xml_strategies.xml_output_strategies.simple_xml_strategy import SimpleXmlOutputStrategy
from prompt_xml_strategies.llm_clients.base_client import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for demonstration purposes."""
    
    def __init__(self):
        super().__init__()
        self.client_type = "MockLLMClient"
        self.model = "mock-model"
    
    def generate_response(self, prompt: str, model: str = "mock-model", **kwargs) -> str:
        """Generate a mock response based on the prompt."""
        # Simulate different responses based on prompt content
        if "analyze" in prompt.lower():
            return """
            {
                "sentiment": "positive",
                "topics": ["artificial intelligence", "technology", "ethics"],
                "summary": "The text discusses the AI revolution's impact on industries, highlighting both opportunities and challenges including ethical considerations and workforce displacement.",
                "key_points": [
                    "AI is transforming multiple industries globally",
                    "Machine learning enables unprecedented automation",
                    "Ethical concerns around bias and privacy are critical",
                    "Human worker displacement is a concern",
                    "Need for fair, transparent, and beneficial AI systems"
                ],
                "confidence": 0.85
            }
            """
        else:
            return """
            {
                "response": "This is a mock response for demonstration purposes.",
                "status": "success",
                "timestamp": "2024-01-15T10:30:00Z"
            }
            """
    
    def validate_connection(self) -> bool:
        """Mock connection validation - always returns True."""
        return True
    
    def get_available_models(self) -> list:
        """Return mock available models."""
        return ["mock-model", "mock-gpt-3.5", "mock-gpt-4"]
    
    def get_client_info(self) -> Dict[str, Any]:
        """Return mock client information."""
        return {
            "client_type": self.client_type,
            "model": self.model,
            "status": "connected",
            "mock": True
        }


def setup_logging() -> logging.Logger:
    """Set up logging for the demo application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('MockDemoApp')


def create_sample_data() -> Dict[str, Any]:
    """Create sample input data for the pipeline."""
    return {
        "task": "analyze_text",
        "text": """
        The artificial intelligence revolution is transforming industries across the globe. 
        From healthcare to finance, AI technologies are enabling unprecedented levels of 
        automation and decision-making capabilities. Machine learning algorithms can now 
        process vast amounts of data to identify patterns and make predictions that would 
        be impossible for humans to achieve manually.
        
        However, this rapid advancement also brings challenges. Ethical considerations around 
        AI bias, privacy concerns, and the potential displacement of human workers are 
        critical issues that society must address. As we move forward, it's essential to 
        develop AI systems that are not only powerful but also fair, transparent, and 
        beneficial to all of humanity.
        """,
        "analysis_type": "sentiment_and_topic",
        "output_format": "structured_summary"
    }


def create_sample_context() -> Dict[str, Any]:
    """Create sample context for the pipeline."""
    return {
        "user_id": "demo_user_123",
        "session_id": "demo_session_456",
        "timestamp": "2024-01-15T10:30:00Z",
        "model_preferences": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }


def create_demo_pipeline(logger: logging.Logger) -> SampleStrategyPipeline:
    """Create and configure a SampleStrategyPipeline for demonstration."""
    
    # Create strategy instances
    prompt_strategy = SimplePromptCreationStrategy()
    response_strategy = SimpleResponseCreationStrategy()
    xml_strategy = SimpleXmlOutputStrategy()
    
    # Create mock LLM client
    llm_client = MockLLMClient()
    
    # Configure pipeline options
    pipeline_options = {
        "enable_timing": True,
        "enable_validation": True,
        "max_retries": 2,
        "retry_delay": 0.5,
        "log_level": "INFO"
    }
    
    # Create the pipeline
    pipeline = SampleStrategyPipeline(
        prompt_strategy=prompt_strategy,
        response_strategy=response_strategy,
        xml_strategy=xml_strategy,
        llm_client=llm_client,
        options=pipeline_options,
        logger=logger
    )
    
    return pipeline


def run_pipeline_demo(pipeline: SampleStrategyPipeline, logger: logging.Logger) -> None:
    """Run the pipeline with sample data and display results."""
    
    logger.info("🚀 Starting SampleStrategyPipeline Mock Demo")
    logger.info("=" * 60)
    
    try:
        # Initialize the pipeline
        logger.info("📋 Initializing pipeline...")
        pipeline.initialize()
        logger.info("✅ Pipeline initialized successfully")
        
        # Prepare sample data
        input_data = create_sample_data()
        context = create_sample_context()
        
        logger.info("📝 Input Data:")
        logger.info(f"   Task: {input_data['task']}")
        logger.info(f"   Analysis Type: {input_data['analysis_type']}")
        logger.info(f"   Text Length: {len(input_data['text'])} characters")
        logger.info("")
        
        # Execute the pipeline
        logger.info("🔄 Executing pipeline...")
        result = pipeline.execute(
            input_data=input_data,
            context=context,
            model="mock-model"
        )
        
        # Display results
        logger.info("✅ Pipeline execution completed successfully!")
        logger.info("=" * 60)
        
        # Show pipeline statistics
        pipeline_info = result.get("pipeline_info", {})
        logger.info("📊 Pipeline Statistics:")
        logger.info(f"   Execution Count: {pipeline_info.get('execution_count', 0)}")
        logger.info(f"   Error Count: {pipeline_info.get('error_count', 0)}")
        logger.info(f"   Success Rate: {pipeline_info.get('success_rate', 0):.2%}")
        
        if pipeline_info.get('average_execution_time'):
            logger.info(f"   Average Execution Time: {pipeline_info['average_execution_time']:.3f}s")
        
        # Show generated content
        logger.info("")
        logger.info("📄 Generated Content:")
        logger.info("-" * 40)
        
        if "prompt" in result:
            logger.info("🤖 Generated Prompt:")
            prompt_preview = result["prompt"][:200] + "..." if len(result["prompt"]) > 200 else result["prompt"]
            logger.info(f"   {prompt_preview}")
            logger.info("")
        
        if "raw_response" in result:
            logger.info("💬 LLM Response:")
            response_preview = result["raw_response"][:300] + "..." if len(result["raw_response"]) > 300 else result["raw_response"]
            logger.info(f"   {response_preview}")
            logger.info("")
        
        if "structured_response" in result:
            logger.info("📋 Structured Response:")
            logger.info(f"   {result['structured_response']}")
            logger.info("")
        
        if "xml_string" in result:
            logger.info("🔧 Generated XML:")
            logger.info(f"   {result['xml_string']}")
            logger.info("")
        
        # Show stage timings if available
        if pipeline_info.get('stage_timings'):
            logger.info("⏱️  Stage Timings:")
            for stage, timing in pipeline_info['stage_timings'].items():
                if isinstance(timing, (int, float)):
                    logger.info(f"   {stage}: {timing:.3f}s")
                else:
                    logger.info(f"   {stage}: {timing}")
            logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Pipeline execution failed: {str(e)}")
        raise
    
    finally:
        # Shutdown the pipeline
        logger.info("🛑 Shutting down pipeline...")
        pipeline.shutdown()
        logger.info("✅ Pipeline shutdown completed")


def main():
    """Main application entry point."""
    print("🎯 SampleStrategyPipeline Mock Demo Application")
    print("=" * 55)
    print("This demo uses a mock LLM client - no external dependencies required!")
    print("=" * 55)
    
    # Set up logging
    logger = setup_logging()
    
    try:
        # Create the pipeline
        logger.info("🔧 Creating SampleStrategyPipeline with mock LLM client...")
        pipeline = create_demo_pipeline(logger)
        
        # Run the demo
        run_pipeline_demo(pipeline, logger)
        
        logger.info("🎉 Mock demo completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Demo failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
