#!/usr/bin/env python3
"""
Question-Answer XML Output Strategy Demo Application

This demo showcases the QAXmlOutputStrategy that generates XML output
using the qa_response.xsd schema for validation.
"""

import os
import sys
import logging
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from prompt_xml_strategies.strategy_pipelines import SampleStrategyPipeline
from prompt_xml_strategies.prompt_strategies.qa_prompt_strategy import QAPromptStrategy
from prompt_xml_strategies.response_strategies.qa_response_strategy import QAResponseStrategy
from prompt_xml_strategies.xml_output_strategies.qa_xml_output_strategy import QAXmlOutputStrategy
from prompt_xml_strategies.llm_clients.base_client import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for demonstration purposes."""
    
    def __init__(self):
        super().__init__()
        self.model_name = "mock-qa-xml-model"
    
    def generate_response(
        self, 
        prompt: str, 
        model: str = None, 
        **kwargs
    ) -> str:
        """Generate a mock response for Q&A XML demo."""
        
        # Simulate different types of responses based on prompt content
        if "artificial intelligence" in prompt.lower():
            return """{
                "answer": "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. It involves developing algorithms and systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, problem-solving, and decision-making.",
                "confidence": 0.95,
                "sources": [
                    {
                        "title": "Artificial Intelligence: A Modern Approach",
                        "url": "https://aima.cs.berkeley.edu/",
                        "type": "book"
                    },
                    {
                        "title": "What is Artificial Intelligence?",
                        "url": "https://www.ibm.com/cloud/learn/what-is-artificial-intelligence",
                        "type": "web"
                    }
                ],
                "follow_up_questions": [
                    "What are the different types of AI?",
                    "How is machine learning related to AI?",
                    "What are some real-world applications of AI?"
                ],
                "explanation": "AI encompasses various subfields including machine learning, natural language processing, computer vision, and robotics. The goal is to create systems that can adapt and improve their performance over time.",
                "examples": [
                    {
                        "description": "Virtual assistants like Siri or Alexa",
                        "code": "// Voice recognition and natural language processing",
                        "output": "Understanding and responding to human speech"
                    },
                    {
                        "description": "Image recognition in photos",
                        "code": "// Computer vision algorithms",
                        "output": "Identifying objects, people, and scenes in images"
                    }
                ],
                "difficulty_level": "intermediate",
                "tags": ["artificial intelligence", "machine learning", "computer science", "algorithms"]
            }"""
        
        elif "machine learning" in prompt.lower():
            return """{
                "answer": "Machine Learning (ML) is a subset of artificial intelligence that focuses on algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience, without being explicitly programmed for every scenario.",
                "confidence": 0.92,
                "sources": [
                    {
                        "title": "The Elements of Statistical Learning",
                        "url": "https://web.stanford.edu/~hastie/ElemStatLearn/",
                        "type": "book"
                    }
                ],
                "follow_up_questions": [
                    "What are the main types of machine learning?",
                    "How do neural networks work?",
                    "What is the difference between supervised and unsupervised learning?"
                ],
                "explanation": "ML algorithms learn patterns from data and make predictions or decisions. The three main types are supervised learning (learning from labeled examples), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through trial and error).",
                "difficulty_level": "intermediate",
                "tags": ["machine learning", "algorithms", "data science", "statistics"]
            }"""
        
        elif "xml" in prompt.lower() or "schema" in prompt.lower():
            return """{
                "answer": "XML (eXtensible Markup Language) is a markup language that defines a set of rules for encoding documents in a format that is both human-readable and machine-readable. XSD (XML Schema Definition) is a language for describing the structure and constraining the contents of XML documents.",
                "confidence": 0.88,
                "sources": [
                    {
                        "title": "XML Schema Definition Language (XSD) 1.1 Part 1: Structures",
                        "url": "https://www.w3.org/TR/xmlschema11-1/",
                        "type": "documentation"
                    },
                    {
                        "title": "XML Tutorial",
                        "url": "https://www.w3schools.com/xml/",
                        "type": "web"
                    }
                ],
                "follow_up_questions": [
                    "What are the benefits of using XSD for validation?",
                    "How does XML differ from JSON?",
                    "What are XML namespaces and why are they important?"
                ],
                "explanation": "XML provides a way to structure data hierarchically with tags, while XSD provides validation rules to ensure XML documents conform to a specific structure. This combination is powerful for data exchange and validation in enterprise applications.",
                "examples": [
                    {
                        "description": "Simple XML document",
                        "code": "<person><name>John Doe</name><age>30</age></person>",
                        "output": "Structured data with clear hierarchy"
                    },
                    {
                        "description": "XSD validation",
                        "code": "<xs:element name=\"name\" type=\"xs:string\"/>",
                        "output": "Defines that 'name' must be a string"
                    }
                ],
                "difficulty_level": "intermediate",
                "tags": ["xml", "xsd", "markup language", "validation", "data structure"]
            }"""
        
        else:
            # Fallback response
            return """{
                "answer": "I understand your question, but I need more specific information to provide a helpful response. Could you please provide more details or clarify what specific aspect you'd like me to address?",
                "confidence": 0.5,
                "sources": [],
                "follow_up_questions": [
                    "Could you be more specific?",
                    "What particular aspect interests you?",
                    "Do you have a specific use case in mind?"
                ],
                "explanation": "This is a general response that requires more context to be truly helpful.",
                "difficulty_level": "beginner",
                "tags": ["general", "clarification"]
            }"""
    
    def validate_connection(self) -> bool:
        """Validate the mock connection."""
        return True
    
    def get_available_models(self) -> list[str]:
        """Get list of available mock models."""
        return ["mock-qa-xml-model", "mock-general-model", "mock-advanced-model"]


def main():
    """Main demo function."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('QAXmlOutputDemo')
    
    print("🎯 Question-Answer XML Output Strategy Demo Application")
    print("=" * 60)
    print("This demo showcases the QAXmlOutputStrategy with XSD schema validation!")
    print("=" * 60)
    
    try:
        # Create the XML output strategy
        logger.info("🔧 Creating QAXmlOutputStrategy...")
        xml_strategy = QAXmlOutputStrategy()
        
        # Create the response strategy
        logger.info("🔧 Creating QAResponseStrategy...")
        response_strategy = QAResponseStrategy()
        
        # Create the prompt strategy
        logger.info("🔧 Creating QAPromptStrategy...")
        prompt_strategy = QAPromptStrategy()
        
        # Create the mock LLM client
        logger.info("🔧 Creating MockLLMClient...")
        llm_client = MockLLMClient()
        
        # Create the pipeline
        logger.info("🔧 Creating SampleStrategyPipeline with QAXmlOutputStrategy...")
        pipeline = SampleStrategyPipeline(
            prompt_strategy=prompt_strategy,
            response_strategy=response_strategy,
            xml_strategy=xml_strategy,
            llm_client=llm_client,
            options={
                'enable_timing': True,
                'enable_validation': True,
                'max_retries': 2,
                'retry_delay': 0.5,
                'log_level': 'INFO'
            }
        )
        
        logger.info("🚀 Starting Question-Answer XML Output Demo")
        logger.info("=" * 60)
        
        # Initialize the pipeline
        logger.info("📋 Initializing pipeline...")
        pipeline.initialize()
        logger.info("✅ Pipeline initialized successfully")
        
        # Test data for Q&A with XML focus
        test_questions = [
            {
                "question": "What is artificial intelligence and how does it work?",
                "user_name": "Alex",
                "assistant_name": "AI Tutor",
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
                "additional_context": "The user is a beginner in AI concepts and prefers detailed explanations with examples."
            },
            {
                "question": "How does machine learning work?",
                "user_name": "Sarah",
                "assistant_name": "ML Expert",
                "system_message": "You are a machine learning expert. Provide technical but accessible explanations.",
                "additional_context": "The user has some programming experience but is new to ML concepts."
            },
            {
                "question": "What is XML and how does XSD schema validation work?",
                "user_name": "Developer",
                "assistant_name": "Tech Expert",
                "system_message": "You are a software development expert. Explain technical concepts clearly with practical examples.",
                "additional_context": "The user is working on a project that involves XML data processing and needs to understand schema validation."
            }
        ]
        
        # Process each question
        for i, question_data in enumerate(test_questions, 1):
            logger.info(f"📝 Question {i}:")
            logger.info(f"   Question: {question_data['question']}")
            logger.info(f"   User: {question_data['user_name']}")
            logger.info(f"   Assistant: {question_data['assistant_name']}")
            if question_data.get('conversation_history'):
                logger.info(f"   Conversation History: {len(question_data['conversation_history'])} messages")
            if question_data.get('additional_context'):
                logger.info(f"   Additional Context: {question_data['additional_context']}")
            logger.info("")
            
            # Show XML strategy info
            xml_info = xml_strategy.get_strategy_info()
            logger.info("📊 XML Output Strategy Information:")
            logger.info(f"   Strategy: {xml_info['name']}")
            logger.info(f"   Version: {xml_info['version']}")
            logger.info(f"   XSD Path: {xml_info['xsd_path']}")
            logger.info(f"   XSD Loaded: {xml_info['xsd_loaded']}")
            logger.info(f"   Namespace: {xml_info['namespace']}")
            logger.info(f"   Supports Validation: {xml_info['supports_validation']}")
            logger.info(f"   Supports Namespaces: {xml_info['supports_namespaces']}")
            
            # Show XSD schema details
            xsd_info = xml_strategy.get_xsd_info()
            if xsd_info['loaded']:
                logger.info("   XSD Schema Details:")
                logger.info(f"      Target Namespace: {xsd_info.get('target_namespace', 'N/A')}")
                logger.info(f"      Elements: {len(xsd_info.get('elements', []))} defined")
                logger.info(f"      Types: {len(xsd_info.get('types', []))} defined")
            logger.info("")
            
            # Execute the pipeline
            logger.info("🔄 Executing pipeline...")
            result = pipeline.execute(
                input_data=question_data,
                model="mock-qa-xml-model",
                temperature=0.7,
                max_tokens=1000
            )
            
            if result:
                logger.info("✅ Pipeline execution completed successfully!")
                logger.info("=" * 60)
                
                # Display the results
                logger.info("📄 Generated Content:")
                logger.info("-" * 40)
                
                # Show the generated prompt
                logger.info("🤖 Generated Prompt:")
                logger.info(f"   {result['prompt'][:200]}...")
                logger.info("")
                
                # Show the LLM response
                logger.info("💬 LLM Response:")
                logger.info(f"   {result['raw_response'][:200]}...")
                logger.info("")
                
                # Show the structured response
                logger.info("📋 Structured Response:")
                if result['structured_response']:
                    logger.info("   Answer:")
                    logger.info(f"      answer: {result['structured_response'].get('answer', 'N/A')}")
                    logger.info(f"      confidence: {result['structured_response'].get('confidence', 'N/A')}")
                    logger.info(f"      sources: {len(result['structured_response'].get('sources', []))} sources")
                    logger.info(f"      follow_up_questions: {len(result['structured_response'].get('follow_up_questions', []))} questions")
                    logger.info(f"      difficulty_level: {result['structured_response'].get('difficulty_level', 'N/A')}")
                    logger.info(f"      tags: {', '.join(result['structured_response'].get('tags', []))}")
                    logger.info("")
                    
                    # Show sources if available
                    if result['structured_response'].get('sources'):
                        logger.info("   Sources:")
                        for j, source in enumerate(result['structured_response']['sources'][:3]):  # Show first 3
                            logger.info(f"      {j+1}. {source.get('title', 'N/A')}")
                            if source.get('url'):
                                logger.info(f"         URL: {source['url']}")
                            if source.get('type'):
                                logger.info(f"         Type: {source['type']}")
                        logger.info("")
                    
                    # Show follow-up questions if available
                    if result['structured_response'].get('follow_up_questions'):
                        logger.info("   Follow-up Questions:")
                        for j, question in enumerate(result['structured_response']['follow_up_questions'][:3]):  # Show first 3
                            logger.info(f"      {j+1}. {question}")
                        logger.info("")
                
                # Show the generated XML
                logger.info("🔧 Generated XML (XSD Schema Validated):")
                if result.get('xml_string'):
                    xml_str = result['xml_string']
                    logger.info(f"   XML Length: {len(xml_str)} characters")
                    logger.info(f"   XML Preview: {xml_str[:300]}...")
                    
                    # Show XML structure analysis
                    logger.info("   XML Structure Analysis:")
                    try:
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(xml_str)
                        logger.info(f"      Root Element: {root.tag}")
                        logger.info(f"      Namespace: {root.tag.split('}')[0][1:] if '}' in root.tag else 'None'}")
                        logger.info(f"      Child Elements: {len(list(root))}")
                        
                        # Show child element details
                        for child in list(root)[:5]:  # Show first 5 children
                            child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                            child_text = child.text[:50] + "..." if child.text and len(child.text) > 50 else child.text
                            logger.info(f"         - {child_tag}: {child_text}")
                        
                        if len(list(root)) > 5:
                            logger.info(f"         ... and {len(list(root)) - 5} more elements")
                            
                    except Exception as e:
                        logger.warning(f"      Could not parse XML for analysis: {e}")
                    
                    logger.info("")
                
                # Show stage timings if available
                if result.get('pipeline_info', {}).get('stage_timings'):
                    logger.info("⏱️  Stage Timings:")
                    for stage, timing_list in result['pipeline_info']['stage_timings'].items():
                        # Assuming timing_list is a list of floats, take the first one for display
                        if timing_list and isinstance(timing_list, list) and isinstance(timing_list[0], (int, float)):
                            logger.info(f"   {stage}: {timing_list[0]:.3f}s")
                        else:
                            logger.info(f"   {stage}: {timing_list}")
                    logger.info("")
                
            else:
                logger.error("❌ Pipeline execution failed!")
                logger.error(f"   Result: {result}")
        
        # Get pipeline statistics
        pipeline_info = pipeline.get_pipeline_info()
        logger.info("📊 Pipeline Statistics:")
        logger.info(f"   Execution Count: {pipeline_info['execution_count']}")
        logger.info(f"   Error Count: {pipeline_info['error_count']}")
        logger.info(f"   Success Rate: {pipeline_info['success_rate']:.2f}%")
        logger.info("")
        
        # Shutdown the pipeline
        logger.info("🛑 Shutting down pipeline...")
        pipeline.shutdown()
        logger.info("✅ Pipeline shutdown completed")
        
        logger.info("🎉 Question-answer XML output demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
