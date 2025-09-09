#!/usr/bin/env python3
"""
Question-Answer Demo Application for SampleStrategyPipeline.

This demo showcases the QAPromptStrategy with the question-answer
JSON schema for conversational AI interactions.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prompt_xml_strategies.strategy_pipelines import SampleStrategyPipeline
from prompt_xml_strategies.prompt_strategies.qa_prompt_strategy import QAPromptStrategy
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
        if "What is artificial intelligence?" in prompt:
            return """
            {
                "answer": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. It encompasses various techniques including machine learning, deep learning, natural language processing, and computer vision.",
                "confidence": 0.95,
                "sources": ["AI textbooks", "research papers"],
                "follow_up_questions": [
                    "What are the different types of AI?",
                    "How does machine learning work?",
                    "What are the applications of AI?"
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
            """
        elif "How does machine learning work?" in prompt:
            return """
            {
                "answer": "Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It works by using algorithms to identify patterns in data, make predictions, and make decisions with minimal human intervention.",
                "confidence": 0.92,
                "sources": ["ML textbooks", "online courses"],
                "follow_up_questions": [
                    "What are the main types of machine learning?",
                    "What is the difference between supervised and unsupervised learning?",
                    "How do neural networks work?"
                ],
                "timestamp": "2024-01-15T10:32:00Z"
            }
            """
        elif "What are the ethical concerns with AI?" in prompt:
            return """
            {
                "answer": "AI raises several ethical concerns including bias and fairness, privacy and surveillance, job displacement, autonomous weapons, and the need for transparency and accountability in AI decision-making processes.",
                "confidence": 0.88,
                "sources": ["AI ethics research", "policy papers"],
                "follow_up_questions": [
                    "How can we ensure AI is fair and unbiased?",
                    "What regulations exist for AI?",
                    "How can we prepare for AI's impact on jobs?"
                ],
                "timestamp": "2024-01-15T10:35:00Z"
            }
            """
        else:
            return """
            {
                "answer": "I understand your question, but I need more specific information to provide a helpful response. Could you please provide more details or clarify what specific aspect you'd like me to address?",
                "confidence": 0.5,
                "sources": [],
                "follow_up_questions": [
                    "Could you be more specific?",
                    "What particular aspect interests you?",
                    "Do you have a specific use case in mind?"
                ],
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
    return logging.getLogger('QuestionAnswerDemo')


def create_sample_data() -> Dict[str, Any]:
    """Create sample input data for the question-answer demo."""
    return {
        "question": "What is artificial intelligence and how does it work?",
        "system_message": "You are a helpful AI assistant specializing in technology and science topics. Provide clear, accurate, and educational responses.",
        "conversation_history": [
            {
                "role": "user",
                "content": "Hi, I'm interested in learning about AI",
                "timestamp": "2024-01-15T10:25:00Z"
            },
            {
                "role": "assistant", 
                "content": "Hello! I'd be happy to help you learn about AI. What specific aspects of artificial intelligence would you like to explore?",
                "timestamp": "2024-01-15T10:25:30Z"
            }
        ],
        "additional_context": "The user is a beginner in AI concepts and prefers detailed explanations with examples.",
        "user_name": "Alex",
        "assistant_name": "AI Tutor"
    }


def create_sample_context() -> Dict[str, Any]:
    """Create sample context for the pipeline."""
    return {
        "user_id": "alex_123",
        "session_id": "qa_session_789",
        "timestamp": "2024-01-15T10:30:00Z",
        "model_preferences": {
            "temperature": 0.7,  # Balanced creativity and accuracy
            "max_tokens": 1500
        },
        "conversation_context": {
            "topic": "artificial_intelligence",
            "user_level": "beginner",
            "preferred_style": "educational"
        }
    }


def create_demo_pipeline(logger: logging.Logger) -> SampleStrategyPipeline:
    """Create and configure a SampleStrategyPipeline for question-answer analysis."""
    
    # Create custom prompt strategy with schema
    prompt_strategy = QAPromptStrategy()
    
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


def run_question_answer_demo(pipeline: SampleStrategyPipeline, logger: logging.Logger) -> None:
    """Run the question-answer analysis demo."""
    
    logger.info("🚀 Starting Question-Answer Analysis Demo")
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
        logger.info(f"   Question: {input_data['question']}")
        logger.info(f"   User: {input_data['user_name']}")
        logger.info(f"   Assistant: {input_data['assistant_name']}")
        logger.info(f"   Conversation History: {len(input_data['conversation_history'])} messages")
        logger.info(f"   Additional Context: {input_data['additional_context']}")
        logger.info("")
        
        # Show schema information
        prompt_strategy = pipeline.prompt_strategy
        schema_info = prompt_strategy.get_strategy_info()
        logger.info("📊 Schema Information:")
        logger.info(f"   Schema Title: {schema_info['schema_title']}")
        logger.info(f"   Schema ID: {schema_info['schema_id']}")
        logger.info(f"   Schema Path: {schema_info['schema_path']}")
        logger.info(f"   Schema Loaded: {schema_info['schema_loaded']}")
        
        # Show schema properties
        properties = prompt_strategy.get_schema_properties()
        logger.info(f"   Available Properties: {len(properties)}")
        for prop_name in properties.keys():
            logger.info(f"     - {prop_name}")
        
        # Show requirements
        requirements = prompt_strategy.get_schema_requirements()
        logger.info(f"   Schema Requirements: {len(requirements)} anyOf groups")
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
            prompt_preview = result["prompt"][:500] + "..." if len(result["prompt"]) > 500 else result["prompt"]
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
                logger.info("   Answer:")
                for key, value in structured.items():
                    if isinstance(value, list):
                        logger.info(f"     {key}: {', '.join(map(str, value))}")
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
    print("🎯 Question-Answer Analysis Demo Application")
    print("=" * 50)
    print("This demo uses a custom QAPromptStrategy with JSON schema!")
    print("=" * 50)
    
    # Set up logging
    logger = setup_logging()
    
    try:
        # Create the pipeline
        logger.info("🔧 Creating SampleStrategyPipeline with QAPromptStrategy...")
        pipeline = create_demo_pipeline(logger)
        
        # Run the demo
        run_question_answer_demo(pipeline, logger)
        
        logger.info("🎉 Question-answer demo completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Demo failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
