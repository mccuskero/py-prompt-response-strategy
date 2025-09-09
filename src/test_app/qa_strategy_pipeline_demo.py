#!/usr/bin/env python3
"""
QA Strategy Pipeline Demo Application

This demo showcases the QAStrategyPipeline that combines QAPromptStrategy,
QAResponseStrategy, and QAXmlOutputStrategy for complete Q&A workflows.
"""

import os
import sys
import logging
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prompt_xml_strategies.strategy_pipelines import QAStrategyPipeline
from prompt_xml_strategies.prompt_strategies.qa_prompt_strategy import QAPromptStrategy
from prompt_xml_strategies.response_strategies.qa_response_strategy import QAResponseStrategy
from prompt_xml_strategies.xml_output_strategies.qa_xml_output_strategy import QAXmlOutputStrategy
from prompt_xml_strategies.llm_clients.base_client import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for demonstration purposes."""
    
    def __init__(self):
        super().__init__()
        self.client_type = "MockQA"
        self.model = "mock-qa-model"
    
    def validate_connection(self) -> bool:
        """Validate connection to the mock LLM service."""
        return True
    
    def generate_response(self, prompt: str, model: str = None, **kwargs) -> str:
        """Generate a mock response for Q&A prompts."""
        # Simulate different responses based on prompt content
        if "artificial intelligence" in prompt.lower():
            return '''{
                "answer": "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. It involves developing algorithms and systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, problem-solving, and decision-making.",
                "confidence": 0.95,
                "sources": [
                    {"title": "Artificial Intelligence: A Modern Approach", "url": "https://aima.cs.berkeley.edu/", "type": "book"},
                    {"title": "What is Artificial Intelligence?", "url": "https://www.ibm.com/cloud/learn/what-is-artificial-intelligence", "type": "web"}
                ],
                "follow_up_questions": [
                    "What are the different types of AI?",
                    "How is machine learning related to AI?",
                    "What are some real-world applications of AI?"
                ],
                "explanation": "AI encompasses various subfields including machine learning, natural language processing, computer vision, and robotics. It has applications in healthcare, finance, transportation, and many other industries.",
                "difficulty_level": "intermediate",
                "tags": ["artificial intelligence", "machine learning", "computer science", "algorithms"]
            }'''
        elif "machine learning" in prompt.lower():
            return '''{
                "answer": "Machine Learning (ML) is a subset of artificial intelligence that focuses on algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience, without being explicitly programmed for every scenario.",
                "confidence": 0.92,
                "sources": [
                    {"title": "The Elements of Statistical Learning", "url": "https://web.stanford.edu/~hastie/ElemStatLearn/", "type": "book"}
                ],
                "follow_up_questions": [
                    "What are the main types of machine learning?",
                    "How do neural networks work?",
                    "What is the difference between supervised and unsupervised learning?"
                ],
                "explanation": "ML algorithms learn patterns from data and make predictions or decisions. The three main types are supervised learning (learning from labeled examples), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through trial and error).",
                "difficulty_level": "intermediate",
                "tags": ["machine learning", "algorithms", "data science", "statistics"]
            }'''
        elif "xml" in prompt.lower() or "xsd" in prompt.lower():
            return '''{
                "answer": "XML (eXtensible Markup Language) is a markup language that defines a set of rules for encoding documents in a format that is both human-readable and machine-readable. XSD (XML Schema Definition) is a language for describing the structure and constraining the contents of XML documents.",
                "confidence": 0.88,
                "sources": [
                    {"title": "XML Schema Tutorial", "url": "https://www.w3schools.com/xml/schema_intro.asp", "type": "web"}
                ],
                "follow_up_questions": [
                    "What are the benefits of using XSD validation?",
                    "How do you create an XSD schema?",
                    "What is the difference between DTD and XSD?"
                ],
                "explanation": "XSD provides a way to define the structure, content, and semantics of XML documents. It allows for data validation, type checking, and documentation of XML formats. XSD is more powerful than DTD as it supports data types, namespaces, and more complex constraints.",
                "difficulty_level": "beginner",
                "tags": ["xml", "xsd", "schema", "validation", "markup"]
            }'''
        else:
            return '''{
                "answer": "I understand your question, but I need more specific information to provide a helpful response. Could you please provide more details or clarify what specific aspect you'd like me to address?",
                "confidence": 0.5,
                "sources": [],
                "follow_up_questions": [
                    "Could you be more specific?",
                    "What particular aspect interests you?",
                    "Do you have a specific use case in mind?"
                ],
                "explanation": "To provide the most accurate and helpful response, I need more context about your question. Please feel free to ask about any specific topic or use case you have in mind.",
                "difficulty_level": "beginner",
                "tags": ["general", "clarification"]
            }'''
    
    def get_available_models(self) -> list[str]:
        """Get list of available mock models."""
        return ["mock-qa-model", "mock-general-model", "mock-advanced-model"]
    
    def get_client_info(self) -> dict:
        """Get information about the mock client."""
        return {
            "client_type": "MockQA",
            "model": self.model,
            "capabilities": ["qa", "conversation", "analysis"]
        }


def main():
    """Main demo function."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("QAStrategyPipelineDemo")
    
    print("🎯 QA Strategy Pipeline Demo Application")
    print("=" * 60)
    print("This demo showcases the complete QA workflow using:")
    print("  • QAPromptStrategy - Schema-validated prompt generation")
    print("  • QAResponseStrategy - Structured response processing")
    print("  • QAXmlOutputStrategy - XSD-validated XML output")
    print("=" * 60)
    
    try:
        # Create strategies
        logger.info("🔧 Creating QA strategies...")
        prompt_strategy = QAPromptStrategy()
        response_strategy = QAResponseStrategy()
        xml_strategy = QAXmlOutputStrategy()
        
        # Create mock LLM client
        logger.info("🔧 Creating MockLLMClient...")
        llm_client = MockLLMClient()
        
        # Create QA strategy pipeline with enhanced options
        logger.info("🔧 Creating QAStrategyPipeline...")
        pipeline = QAStrategyPipeline(
            prompt_strategy=prompt_strategy,
            response_strategy=response_strategy,
            xml_strategy=xml_strategy,
            llm_client=llm_client,
            options={
                'enable_timing': True,
                'enable_validation': True,
                'max_retries': 2,
                'retry_delay': 0.5,
                'log_level': 'INFO',
                'conversation_context': True,
                'response_enhancement': True,
                'xml_validation': True,
                'metadata_tracking': True
            }
        )
        
        logger.info("🚀 Starting QA Strategy Pipeline Demo")
        logger.info("=" * 60)
        
        # Initialize pipeline
        logger.info("📋 Initializing pipeline...")
        pipeline.initialize()
        logger.info("✅ Pipeline initialized successfully")
        
        # Sample Q&A scenarios
        qa_scenarios = [
            {
                "question": "What is artificial intelligence and how does it work?",
                "user_name": "Alex",
                "assistant_name": "AI Tutor",
                "conversation_history": [
                    {"role": "user", "content": "Hi, I'm interested in learning about AI", "timestamp": "2024-01-15T10:25:00Z"},
                    {"role": "assistant", "content": "Hello! I'd be happy to help you learn about AI. What specific aspects of artificial intelligence would you like to explore?", "timestamp": "2024-01-15T10:25:30Z"}
                ],
                "additional_context": "The user is a beginner in AI concepts and prefers detailed explanations with examples."
            },
            {
                "question": "How does machine learning work?",
                "user_name": "Sarah",
                "assistant_name": "ML Expert",
                "additional_context": "The user has some programming experience but is new to ML concepts."
            },
            {
                "question": "What is XML and how does XSD schema validation work?",
                "user_name": "Developer",
                "assistant_name": "Tech Expert",
                "additional_context": "The user is working on a project that involves XML data processing and needs to understand schema validation."
            }
        ]
        
        # Process each Q&A scenario
        for i, scenario in enumerate(qa_scenarios, 1):
            logger.info(f"📝 Q&A Scenario {i}:")
            logger.info(f"   Question: {scenario['question']}")
            logger.info(f"   User: {scenario['user_name']}")
            logger.info(f"   Assistant: {scenario['assistant_name']}")
            if 'conversation_history' in scenario:
                logger.info(f"   Conversation History: {len(scenario['conversation_history'])} messages")
            logger.info(f"   Additional Context: {scenario['additional_context']}")
            logger.info("")
            
            # Log QA-specific configuration
            logger.info("📊 QA Pipeline Configuration:")
            logger.info(f"   Conversation Context: {pipeline.qa_config['conversation_context']}")
            logger.info(f"   Response Enhancement: {pipeline.qa_config['response_enhancement']}")
            logger.info(f"   XML Validation: {pipeline.qa_config['xml_validation']}")
            logger.info(f"   Metadata Tracking: {pipeline.qa_config['metadata_tracking']}")
            logger.info("")
            
            # Execute pipeline
            logger.info("🔄 Executing QA pipeline...")
            result = pipeline.execute(scenario)
            
            if result:
                logger.info("✅ QA pipeline execution completed successfully!")
                logger.info("=" * 60)
                logger.info("📄 Generated Content:")
                logger.info("-" * 40)
                
                # Display generated prompt
                logger.info("🤖 Generated Prompt:")
                logger.info(f"   {result['prompt'][:200]}...")
                logger.info("")
                
                # Display LLM response
                logger.info("💬 LLM Response:")
                logger.info(f"   {result['raw_response'][:200]}...")
                logger.info("")
                
                # Display structured response
                structured = result['structured_response']
                logger.info("📋 Structured Response:")
                logger.info(f"   Answer: {structured.get('answer', 'N/A')[:100]}...")
                logger.info(f"   Confidence: {structured.get('confidence', 'N/A')}")
                logger.info(f"   Sources: {len(structured.get('sources', []))} sources")
                logger.info(f"   Follow-up Questions: {len(structured.get('follow_up_questions', []))} questions")
                logger.info(f"   Difficulty Level: {structured.get('difficulty_level', 'N/A')}")
                logger.info(f"   Tags: {', '.join(structured.get('tags', []))}")
                logger.info("")
                
                # Display XML output
                xml_element = result['xml_element']
                logger.info("🔧 Generated XML (XSD Schema Validated):")
                logger.info(f"   XML Root Element: {xml_element.tag}")
                logger.info(f"   XML Children Count: {len(xml_element)}")
                logger.info(f"   XML Namespace: {xml_element.tag.split('}')[0] if '}' in xml_element.tag else 'default'}")
                logger.info("")
                
                # Display timing information
                if 'pipeline_info' in result and 'stage_timings' in result['pipeline_info']:
                    timings = result['pipeline_info']['stage_timings']
                    logger.info("⏱️  Stage Timings:")
                    for stage, timing_list in timings.items():
                        if timing_list:
                            avg_time = sum(timing_list) / len(timing_list)
                            logger.info(f"   {stage}: {avg_time:.3f}s")
                    logger.info("")
            else:
                logger.error("❌ QA pipeline execution failed!")
                logger.error(f"   Result: {result}")
            
            logger.info("=" * 60)
            logger.info("")
        
        # Display pipeline statistics
        logger.info("📊 QA Pipeline Statistics:")
        logger.info(f"   Total Questions Processed: {pipeline._execution_count}")
        logger.info(f"   Successful QA Workflows: {pipeline._execution_count - pipeline._error_count}")
        logger.info(f"   Failed QA Workflows: {pipeline._error_count}")
        logger.info(f"   QA Success Rate: {((pipeline._execution_count - pipeline._error_count) / max(pipeline._execution_count, 1)) * 100:.1f}%")
        logger.info("")
        
        # Get QA-specific metrics
        qa_metrics = pipeline.get_qa_metrics()
        logger.info("📈 QA-Specific Metrics:")
        logger.info(f"   Average QA Processing Time: {qa_metrics['average_qa_processing_time']:.3f}s")
        logger.info(f"   QA Configuration: {qa_metrics['qa_configuration']}")
        logger.info("")
        
        # Shutdown pipeline
        logger.info("🛑 Shutting down QA pipeline...")
        pipeline.shutdown()
        logger.info("✅ QA pipeline shutdown completed")
        logger.info("🎉 QA Strategy Pipeline demo completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Demo failed: {str(e)}")
        logger.exception("Full error details:")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
