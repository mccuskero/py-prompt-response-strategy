#!/usr/bin/env python3
"""
Event Timeline Demo Application for SampleStrategyPipeline.

This demo showcases the EventTimelinePromptStrategy with a custom JSON schema
for analyzing event sequences and temporal relationships.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prompt_xml_strategies.strategy_pipelines import SampleStrategyPipeline
from event_timeline_prompt_strategy import EventTimelinePromptStrategy
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
        if "Event Timeline" in prompt:
            return """
            {
                "temporal_analysis": {
                    "total_duration": "00:04:00",
                    "average_event_interval": "24.0",
                    "longest_gap": "30",
                    "shortest_gap": "15"
                },
                "critical_path": [
                    "event_001", "event_002", "event_003", "event_004", "event_005", "event_010"
                ],
                "parallel_events": [
                    ["event_002", "event_003"],
                    ["event_008", "event_009"]
                ],
                "performance_insights": {
                    "bottlenecks": ["event_001", "event_004"],
                    "optimization_opportunities": [
                        "Parallelize database connection and authentication service loading",
                        "Start cache warming earlier in the process",
                        "Implement health checks before full startup"
                    ]
                },
                "dependencies": {
                    "event_002": ["event_001"],
                    "event_003": ["event_001"],
                    "event_004": ["event_002", "event_003"],
                    "event_005": ["event_004"],
                    "event_006": ["event_005"],
                    "event_007": ["event_006"],
                    "event_008": ["event_007"],
                    "event_009": ["event_007"],
                    "event_010": ["event_008", "event_009"]
                },
                "summary": "The system startup follows a logical sequence with clear dependencies. The critical path shows a 4-minute startup time, with opportunities for parallelization in the authentication and caching phases. The longest gap occurs between API registration and web server startup, suggesting potential optimization."
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
    return logging.getLogger('EventTimelineDemo')


def create_sample_data() -> Dict[str, Any]:
    """Create sample input data for the event timeline analysis."""
    return {
        "analysis_type": "performance",
        "focus_areas": ["critical_path", "bottlenecks", "optimization"],
        "output_format": "structured",
        "timeline_id": "system_startup_001",
        "analysis_depth": "comprehensive"
    }


def create_sample_context() -> Dict[str, Any]:
    """Create sample context for the pipeline."""
    return {
        "user_id": "timeline_analyst_123",
        "session_id": "timeline_session_456",
        "timestamp": "2024-01-15T10:30:00Z",
        "model_preferences": {
            "temperature": 0.3,  # Lower temperature for more focused analysis
            "max_tokens": 2000
        },
        "analysis_context": {
            "system_type": "web_application",
            "environment": "production",
            "scale": "enterprise"
        }
    }


def create_demo_pipeline(logger: logging.Logger) -> SampleStrategyPipeline:
    """Create and configure a SampleStrategyPipeline for event timeline analysis."""
    
    # Create custom prompt strategy with schema
    prompt_strategy = EventTimelinePromptStrategy()
    
    # Create other strategy instances
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


def run_event_timeline_demo(pipeline: SampleStrategyPipeline, logger: logging.Logger) -> None:
    """Run the event timeline analysis demo."""
    
    logger.info("🚀 Starting Event Timeline Analysis Demo")
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
        logger.info(f"   Analysis Type: {input_data['analysis_type']}")
        logger.info(f"   Focus Areas: {', '.join(input_data['focus_areas'])}")
        logger.info(f"   Timeline ID: {input_data['timeline_id']}")
        logger.info("")
        
        # Show schema information
        prompt_strategy = pipeline.prompt_strategy
        schema_info = prompt_strategy.get_strategy_info()
        logger.info("📊 Schema Information:")
        logger.info(f"   Schema Name: {schema_info['schema_name']}")
        logger.info(f"   Schema Path: {schema_info['schema_path']}")
        logger.info(f"   Schema Loaded: {schema_info['schema_loaded']}")
        
        # Show event count
        events = prompt_strategy.get_schema_events()
        metadata = prompt_strategy.get_schema_metadata()
        logger.info(f"   Total Events: {len(events)}")
        logger.info(f"   Time Span: {metadata.get('time_span', 'Unknown')}")
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
            prompt_preview = result["prompt"][:300] + "..." if len(result["prompt"]) > 300 else result["prompt"]
            logger.info(f"   {prompt_preview}")
            logger.info("")
        
        if "raw_response" in result:
            logger.info("💬 LLM Response:")
            response_preview = result["raw_response"][:400] + "..." if len(result["raw_response"]) > 400 else result["raw_response"]
            logger.info(f"   {response_preview}")
            logger.info("")
        
        if "structured_response" in result:
            logger.info("📋 Structured Response:")
            structured = result['structured_response']
            if isinstance(structured, dict):
                logger.info("   Analysis Results:")
                for key, value in structured.items():
                    if isinstance(value, dict):
                        logger.info(f"     {key}:")
                        for sub_key, sub_value in value.items():
                            logger.info(f"       {sub_key}: {sub_value}")
                    elif isinstance(value, list):
                        logger.info(f"     {key}: {value}")
                    else:
                        logger.info(f"     {key}: {value}")
            else:
                logger.info(f"   {structured}")
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
    print("🎯 Event Timeline Analysis Demo Application")
    print("=" * 50)
    print("This demo uses a custom EventTimelinePromptStrategy with JSON schema!")
    print("=" * 50)
    
    # Set up logging
    logger = setup_logging()
    
    try:
        # Create the pipeline
        logger.info("🔧 Creating SampleStrategyPipeline with EventTimelinePromptStrategy...")
        pipeline = create_demo_pipeline(logger)
        
        # Run the demo
        run_event_timeline_demo(pipeline, logger)
        
        logger.info("🎉 Event timeline demo completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Demo failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
