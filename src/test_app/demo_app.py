#!/usr/bin/env python3
"""
Demo application showcasing SampleStrategyPipeline functionality.

This application demonstrates how to use the SampleStrategyPipeline
with sample text to generate structured XML output through the
three-tier strategy system.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prompt_xml_strategies.strategy_pipelines import SampleStrategyPipeline
from prompt_xml_strategies.prompt_strategies.simple_prompt_strategy import SimplePromptCreationStrategy
from prompt_xml_strategies.response_strategies.simple_response_strategy import SimpleResponseCreationStrategy
from prompt_xml_strategies.xml_output_strategies.simple_xml_strategy import SimpleXmlOutputStrategy
from prompt_xml_strategies.llm_clients.openwebui_client import OpenWebUIClient


def setup_logging() -> logging.Logger:
    """Set up logging for the demo application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('demo_app.log')
        ]
    )
    return logging.getLogger('DemoApp')


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
    
    # Create LLM client (using OpenWebUI for demo)
    llm_client = OpenWebUIClient(
        base_url="http://localhost:8080",  # Default OpenWebUI URL
        api_key="demo_key"  # Demo key for testing
    )
    
    # Configure pipeline options
    pipeline_options = {
        "enable_timing": True,
        "enable_validation": True,
        "max_retries": 3,
        "retry_delay": 1.0,
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
    
    logger.info("🚀 Starting SampleStrategyPipeline Demo")
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
            model="gpt-3.5-turbo"  # Demo model
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
                logger.info(f"   {stage}: {timing:.3f}s")
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
    print("🎯 SampleStrategyPipeline Demo Application")
    print("=" * 50)
    
    # Set up logging
    logger = setup_logging()
    
    try:
        # Create the pipeline
        logger.info("🔧 Creating SampleStrategyPipeline...")
        pipeline = create_demo_pipeline(logger)
        
        # Run the demo
        run_pipeline_demo(pipeline, logger)
        
        logger.info("🎉 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Demo failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
