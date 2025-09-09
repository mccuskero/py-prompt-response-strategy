"""Tests for the QAPromptStrategy class."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from prompt_xml_strategies.prompt_strategies.qa_prompt_strategy import QAPromptStrategy


class TestQAPromptStrategy:
    """Test cases for QAPromptStrategy class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary schema file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.schema_file = os.path.join(self.temp_dir, "test_schema.json")
        
        # Sample schema data
        self.schema_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://test.dev/schemas/question-answer.json",
            "title": "Test Question-Answer Prompt Schema",
            "description": "Test schema for question-answer prompts",
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The main question to ask",
                    "minLength": 1
                },
                "user_input": {
                    "type": "string", 
                    "description": "Alternative user input field",
                    "minLength": 1
                },
                "system_message": {
                    "type": "string",
                    "description": "System message to set context or behavior"
                },
                "conversation_history": {
                    "type": "array",
                    "description": "Previous messages in the conversation",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["user", "assistant", "system"]
                            },
                            "content": {
                                "type": "string",
                                "minLength": 1
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time"
                            }
                        },
                        "required": ["role", "content"]
                    }
                },
                "additional_context": {
                    "type": "string",
                    "description": "Additional context information"
                },
                "user_name": {
                    "type": "string",
                    "description": "Name of the user"
                },
                "assistant_name": {
                    "type": "string", 
                    "description": "Name of the assistant"
                }
            },
            "anyOf": [
                {"required": ["question"]},
                {"required": ["user_input"]},
                {"required": ["conversation_history"]}
            ]
        }
        
        # Write schema to temporary file
        with open(self.schema_file, 'w') as f:
            json.dump(self.schema_data, f)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_custom_schema_path(self):
        """Test initialization with custom schema path."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        assert strategy.schema_path == self.schema_file
        assert strategy.schema_data is not None
        assert strategy.schema_data["title"] == "Test Question-Answer Prompt Schema"
    
    def test_initialization_with_default_schema_path(self):
        """Test initialization with default schema path."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(self.schema_data))):
                strategy = QAPromptStrategy()
                
                assert strategy.schema_path is not None
                assert strategy.schema_data is not None
    
    def test_initialization_schema_file_not_found(self):
        """Test initialization when schema file is not found."""
        with pytest.raises(FileNotFoundError):
            QAPromptStrategy(schema_path="nonexistent.json")
    
    def test_initialization_invalid_json(self):
        """Test initialization with invalid JSON schema."""
        invalid_schema_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_schema_file, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(ValueError, match="Invalid JSON in schema file"):
            QAPromptStrategy(schema_path=invalid_schema_file)
    
    def test_create_prompt_with_question(self):
        """Test prompt creation with question input."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "question": "What is artificial intelligence?",
            "user_name": "Alice",
            "assistant_name": "AI Assistant"
        }
        
        prompt = strategy.create_prompt(input_data)
        
        assert "What is artificial intelligence?" in prompt
        assert "Alice:" in prompt
        assert "Please provide a helpful and accurate response" in prompt
    
    def test_create_prompt_with_user_input(self):
        """Test prompt creation with user_input instead of question."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "user_input": "How does machine learning work?",
            "user_name": "Bob",
            "assistant_name": "ML Expert"
        }
        
        prompt = strategy.create_prompt(input_data)
        
        assert "How does machine learning work?" in prompt
        assert "Bob:" in prompt
    
    def test_create_prompt_with_system_message(self):
        """Test prompt creation with system message."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "question": "What is Python?",
            "system_message": "You are a programming tutor. Explain concepts clearly.",
            "user_name": "Student"
        }
        
        prompt = strategy.create_prompt(input_data)
        
        assert "System: You are a programming tutor" in prompt
        assert "What is Python?" in prompt
        assert "Student:" in prompt
    
    def test_create_prompt_with_conversation_history(self):
        """Test prompt creation with conversation history."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "question": "Can you explain more?",
            "conversation_history": [
                {
                    "role": "user",
                    "content": "What is AI?",
                    "timestamp": "2024-01-15T10:00:00Z"
                },
                {
                    "role": "assistant",
                    "content": "AI is artificial intelligence...",
                    "timestamp": "2024-01-15T10:00:30Z"
                }
            ],
            "user_name": "User",
            "assistant_name": "Assistant"
        }
        
        prompt = strategy.create_prompt(input_data)
        
        assert "Conversation History:" in prompt
        assert "User (2024-01-15T10:00:00Z): What is AI?" in prompt
        assert "Assistant (2024-01-15T10:00:30Z): AI is artificial intelligence..." in prompt
        assert "User: Can you explain more?" in prompt
    
    def test_create_prompt_with_additional_context(self):
        """Test prompt creation with additional context."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "question": "What is the best approach?",
            "additional_context": "The user is a beginner in programming",
            "user_name": "Newbie"
        }
        
        prompt = strategy.create_prompt(input_data)
        
        assert "Context: The user is a beginner in programming" in prompt
        assert "What is the best approach?" in prompt
    
    def test_create_prompt_with_context_parameter(self):
        """Test prompt creation with context parameter."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {"question": "What is testing?"}
        context = {"topic": "software_development", "level": "intermediate"}
        
        prompt = strategy.create_prompt(input_data, context)
        
        assert "Additional Context:" in prompt
        assert "topic: software_development" in prompt
        assert "level: intermediate" in prompt
    
    def test_create_prompt_without_question_or_user_input(self):
        """Test prompt creation with only conversation history."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        prompt = strategy.create_prompt(input_data)
        
        assert "Conversation History:" in prompt
        assert "Hello" in prompt
        assert "Hi there!" in prompt
    
    def test_get_strategy_info(self):
        """Test getting strategy information."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        info = strategy.get_strategy_info()
        
        assert info["name"] == "QAPromptStrategy"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Generates conversational prompts using question-answer schema"
        assert info["schema_path"] == self.schema_file
        assert info["schema_loaded"] is True
        assert info["schema_title"] == "Test Question-Answer Prompt Schema"
        assert info["schema_id"] == "https://test.dev/schemas/question-answer.json"
    
    def test_validate_input_valid_question(self):
        """Test input validation with valid question."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {"question": "What is testing?"}
        
        assert strategy.validate_input(input_data) is True
    
    def test_validate_input_valid_user_input(self):
        """Test input validation with valid user_input."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {"user_input": "How do I learn programming?"}
        
        assert strategy.validate_input(input_data) is True
    
    def test_validate_input_valid_conversation_history(self):
        """Test input validation with valid conversation history."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ]
        }
        
        assert strategy.validate_input(input_data) is True
    
    def test_validate_input_invalid_no_required_fields(self):
        """Test input validation with no required fields."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {"system_message": "Just a system message"}
        
        assert strategy.validate_input(input_data) is False
    
    def test_validate_input_invalid_question_type(self):
        """Test input validation with invalid question type."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {"question": 123}  # Should be string
        
        assert strategy.validate_input(input_data) is False
    
    def test_validate_input_invalid_conversation_history(self):
        """Test input validation with invalid conversation history."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "conversation_history": [
                {"role": "invalid_role", "content": "Hello"}  # Invalid role
            ]
        }
        
        assert strategy.validate_input(input_data) is False
    
    def test_validate_input_invalid_input_type(self):
        """Test input validation with invalid input type."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        assert strategy.validate_input("not a dict") is False
    
    def test_get_template_variables(self):
        """Test getting template variables."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        variables = strategy.get_template_variables()
        
        expected_variables = [
            'question', 'user_input', 'system_message', 'conversation_history',
            'additional_context', 'user_name', 'assistant_name'
        ]
        
        assert set(variables) == set(expected_variables)
    
    def test_reload_schema(self):
        """Test reloading schema from file."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        # Create a new schema file
        new_schema_file = os.path.join(self.temp_dir, "new_schema.json")
        new_schema_data = self.schema_data.copy()
        new_schema_data["title"] = "Updated Schema Title"
        
        with open(new_schema_file, 'w') as f:
            json.dump(new_schema_data, f)
        
        # Reload with new schema
        strategy.reload_schema(new_schema_file)
        
        assert strategy.schema_path == new_schema_file
        assert strategy.schema_data["title"] == "Updated Schema Title"
    
    def test_get_schema_properties(self):
        """Test getting schema properties."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        properties = strategy.get_schema_properties()
        
        assert "question" in properties
        assert "user_input" in properties
        assert "system_message" in properties
        assert "conversation_history" in properties
        assert "additional_context" in properties
        assert "user_name" in properties
        assert "assistant_name" in properties
    
    def test_get_schema_requirements(self):
        """Test getting schema requirements."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        requirements = strategy.get_schema_requirements()
        
        assert len(requirements) == 3
        assert {"required": ["question"]} in requirements
        assert {"required": ["user_input"]} in requirements
        assert {"required": ["conversation_history"]} in requirements
    
    def test_create_prompt_with_empty_schema_data(self):
        """Test prompt creation when schema data is not loaded."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        strategy.schema_data = None
        
        with pytest.raises(ValueError, match="Schema not loaded"):
            strategy.create_prompt({"question": "test"})
    
    def test_create_prompt_with_complex_conversation(self):
        """Test prompt creation with complex conversation history."""
        strategy = QAPromptStrategy(schema_path=self.schema_file)
        
        input_data = {
            "question": "Can you summarize our discussion?",
            "system_message": "You are a helpful assistant.",
            "conversation_history": [
                {"role": "user", "content": "What is AI?", "timestamp": "2024-01-15T10:00:00Z"},
                {"role": "assistant", "content": "AI is artificial intelligence...", "timestamp": "2024-01-15T10:00:30Z"},
                {"role": "user", "content": "What are the types?", "timestamp": "2024-01-15T10:01:00Z"},
                {"role": "assistant", "content": "There are several types...", "timestamp": "2024-01-15T10:01:30Z"},
                {"role": "system", "content": "User seems interested in learning more", "timestamp": "2024-01-15T10:02:00Z"}
            ],
            "additional_context": "User is a student learning about AI",
            "user_name": "Student",
            "assistant_name": "AI Tutor"
        }
        
        prompt = strategy.create_prompt(input_data)
        
        # Check that all elements are present
        assert "System: You are a helpful assistant." in prompt
        assert "Context: User is a student learning about AI" in prompt
        assert "Conversation History:" in prompt
        assert "Student (2024-01-15T10:00:00Z): What is AI?" in prompt
        assert "AI Tutor (2024-01-15T10:00:30Z): AI is artificial intelligence..." in prompt
        assert "System (2024-01-15T10:02:00Z): User seems interested in learning more" in prompt
        assert "Student: Can you summarize our discussion?" in prompt
        assert "Please provide a helpful and accurate response" in prompt
