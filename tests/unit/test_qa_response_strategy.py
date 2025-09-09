"""Tests for the QAResponseStrategy class."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from prompt_xml_strategies.response_strategies.qa_response_strategy import QAResponseStrategy


class TestQAResponseStrategy:
    """Test cases for QAResponseStrategy class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary schema file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.schema_file = os.path.join(self.temp_dir, "test_qa_schema.json")
        
        # Sample schema data
        self.schema_data = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://test.dev/schemas/qa-response.json",
            "title": "Test Q&A Response Schema",
            "description": "Test schema for Q&A responses",
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "The main answer to the question",
                    "minLength": 1
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence level in the answer (0-1)",
                    "minimum": 0,
                    "maximum": 1
                },
                "sources": {
                    "type": "array",
                    "description": "Sources or references for the answer",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "type": {"type": "string", "enum": ["web", "book", "paper", "documentation"]}
                        },
                        "required": ["title"]
                    }
                },
                "follow_up_questions": {
                    "type": "array",
                    "description": "Suggested follow-up questions",
                    "items": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "explanation": {
                    "type": "string",
                    "description": "Detailed explanation or reasoning"
                },
                "examples": {
                    "type": "array",
                    "description": "Examples to illustrate the answer",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "code": {"type": "string"},
                            "output": {"type": "string"}
                        },
                        "required": ["description"]
                    }
                },
                "difficulty_level": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "advanced"],
                    "description": "Complexity level of the answer"
                },
                "tags": {
                    "type": "array",
                    "description": "Topic tags for categorization",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["answer"],
            "additionalProperties": False
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
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        assert strategy.schema_path == self.schema_file
        assert strategy.schema_data is not None
        assert strategy.schema_data["title"] == "Test Q&A Response Schema"
    
    def test_initialization_with_default_schema_path(self):
        """Test initialization with default schema path."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(self.schema_data))):
                strategy = QAResponseStrategy()
                
                assert strategy.schema_path is not None
                assert strategy.schema_data is not None
    
    def test_initialization_schema_file_not_found(self):
        """Test initialization when schema file is not found."""
        with pytest.raises(FileNotFoundError):
            QAResponseStrategy(schema_path="nonexistent.json")
    
    def test_initialization_invalid_json(self):
        """Test initialization with invalid JSON schema."""
        invalid_schema_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_schema_file, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(ValueError, match="Invalid JSON in schema file"):
            QAResponseStrategy(schema_path=invalid_schema_file)
    
    def test_process_response_with_valid_json(self):
        """Test processing a valid JSON response."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response_data = {
            "answer": "Python is a programming language",
            "confidence": 0.9,
            "sources": [{"title": "Python.org", "url": "https://python.org", "type": "web"}],
            "follow_up_questions": ["What can you build with Python?", "How do I learn Python?"],
            "explanation": "Python is widely used for web development, data science, and automation.",
            "difficulty_level": "beginner",
            "tags": ["python", "programming"]
        }
        
        raw_response = json.dumps(response_data)
        processed = strategy.process_response(raw_response)
        
        assert processed["answer"] == "Python is a programming language"
        assert processed["confidence"] == 0.9
        assert len(processed["sources"]) == 1
        assert len(processed["follow_up_questions"]) == 2
        assert "_metadata" in processed
        assert processed["_metadata"]["processed_by"] == "QAResponseStrategy"
    
    def test_process_response_with_json_code_block(self):
        """Test processing a response with JSON in code blocks."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response_data = {
            "answer": "Machine learning is a subset of AI",
            "confidence": 0.8
        }
        
        raw_response = f"Here's the structured response:\n```json\n{json.dumps(response_data)}\n```\nThis is additional text."
        processed = strategy.process_response(raw_response)
        
        assert processed["answer"] == "Machine learning is a subset of AI"
        assert processed["confidence"] == 0.8
        assert "_metadata" in processed
    
    def test_process_response_fallback_text(self):
        """Test processing a non-JSON response with fallback."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        raw_response = "Python is a high-level programming language that is easy to learn and widely used in data science and web development."
        processed = strategy.process_response(raw_response)
        
        assert "answer" in processed
        assert "confidence" in processed
        assert processed["confidence"] == 0.3  # Lower confidence for fallback
        assert processed["_metadata"]["fallback_used"] is True
        assert "python" in processed["tags"]  # Should extract tags
    
    def test_validate_response_valid(self):
        """Test validation of a valid response."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "This is a valid answer",
            "confidence": 0.8,
            "sources": [{"title": "Test Source"}],
            "follow_up_questions": ["What else?"],
            "difficulty_level": "intermediate",
            "tags": ["test"]
        }
        
        assert strategy.validate_response(response) is True
    
    def test_validate_response_missing_required_field(self):
        """Test validation with missing required field."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "confidence": 0.8
            # Missing required "answer" field
        }
        
        with pytest.raises(Exception, match="Response must contain an 'answer' field"):
            strategy.validate_response(response)
    
    def test_validate_response_invalid_confidence(self):
        """Test validation with invalid confidence value."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "This is an answer",
            "confidence": 1.5  # Invalid confidence > 1
        }
        
        with pytest.raises(Exception, match="Confidence must be between 0 and 1"):
            strategy.validate_response(response)
    
    def test_validate_response_invalid_difficulty_level(self):
        """Test validation with invalid difficulty level."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "This is an answer",
            "difficulty_level": "expert"  # Invalid level
        }
        
        with pytest.raises(Exception, match="Difficulty level must be 'beginner', 'intermediate', or 'advanced'"):
            strategy.validate_response(response)
    
    def test_validate_response_invalid_sources(self):
        """Test validation with invalid sources format."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "This is an answer",
            "sources": "not a list"  # Should be a list
        }
        
        with pytest.raises(Exception, match="Sources must be a list"):
            strategy.validate_response(response)
    
    def test_validate_response_invalid_follow_up_questions(self):
        """Test validation with invalid follow-up questions format."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "This is an answer",
            "follow_up_questions": "not a list"  # Should be a list
        }
        
        with pytest.raises(Exception, match="Follow-up questions must be a list"):
            strategy.validate_response(response)
    
    def test_validate_response_invalid_tags(self):
        """Test validation with invalid tags format."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "This is an answer",
            "tags": "not a list"  # Should be a list
        }
        
        with pytest.raises(Exception, match="Tags must be a list"):
            strategy.validate_response(response)
    
    def test_validate_response_invalid_input_type(self):
        """Test validation with invalid input type."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        with pytest.raises(Exception, match="Response must be a dictionary"):
            strategy.validate_response("not a dict")
    
    def test_get_strategy_info(self):
        """Test getting strategy information."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        info = strategy.get_strategy_info()
        
        assert info["name"] == "QAResponseStrategy"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Processes Q&A responses using JSON schema validation"
        assert info["schema_path"] == self.schema_file
        assert info["schema_loaded"] is True
        assert info["schema_title"] == "Test Q&A Response Schema"
        assert info["schema_id"] == "https://test.dev/schemas/qa-response.json"
        assert info["supports_json"] is True
        assert info["supports_fallback"] is True
        assert info["supports_validation"] is True
    
    def test_get_schema_properties(self):
        """Test getting schema properties."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        properties = strategy.get_schema_properties()
        
        expected_properties = [
            'answer', 'confidence', 'sources', 'follow_up_questions',
            'explanation', 'examples', 'difficulty_level', 'tags'
        ]
        
        assert set(properties) == set(expected_properties)
    
    def test_get_schema_requirements(self):
        """Test getting schema requirements."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        requirements = strategy.get_schema_requirements()
        
        assert requirements == ["answer"]
    
    def test_reload_schema(self):
        """Test reloading schema from file."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        # Create a new schema file
        new_schema_file = os.path.join(self.temp_dir, "new_qa_schema.json")
        new_schema_data = self.schema_data.copy()
        new_schema_data["title"] = "Updated Q&A Schema Title"
        
        with open(new_schema_file, 'w') as f:
            json.dump(new_schema_data, f)
        
        # Reload with new schema
        strategy.reload_schema(new_schema_file)
        
        assert strategy.schema_path == new_schema_file
        assert strategy.schema_data["title"] == "Updated Q&A Schema Title"
    
    def test_extract_answer_from_text(self):
        """Test answer extraction from text."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        text = "This is a comprehensive answer about Python programming.\nIt covers multiple aspects."
        answer = strategy._extract_answer_from_text(text)
        
        assert "comprehensive answer about Python programming" in answer
    
    def test_extract_follow_up_questions(self):
        """Test follow-up question extraction."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        text = "Python is great. What about performance? How about memory usage? Can you explain optimization?"
        questions = strategy._extract_follow_up_questions(text)
        
        assert len(questions) > 0
        assert any("performance" in q.lower() for q in questions)
        assert any("memory usage" in q.lower() for q in questions)
    
    def test_assess_difficulty_level(self):
        """Test difficulty level assessment."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        # Test advanced
        advanced_text = "This involves complex algorithms and optimization techniques."
        assert strategy._assess_difficulty_level(advanced_text) == "advanced"
        
        # Test beginner
        beginner_text = "This is a simple and basic introduction to programming."
        assert strategy._assess_difficulty_level(beginner_text) == "beginner"
        
        # Test intermediate (default)
        intermediate_text = "This is a moderate explanation of the topic."
        assert strategy._assess_difficulty_level(intermediate_text) == "intermediate"
    
    def test_extract_tags(self):
        """Test tag extraction from text."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        text = "This is about Python programming and machine learning with data science applications."
        tags = strategy._extract_tags(text)
        
        assert "python" in tags
        assert "machine learning" in tags
        assert "data science" in tags
        assert len(tags) <= 5  # Should be limited to 5 tags
    
    def test_enhance_response(self):
        """Test response enhancement with metadata."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "Test answer",
            "confidence": 0.8
        }
        
        context = {"user_id": "test_user"}
        enhanced = strategy._enhance_response(response, context)
        
        assert enhanced["answer"] == "Test answer"
        assert enhanced["confidence"] == 0.8
        assert "_metadata" in enhanced
        assert enhanced["_metadata"]["processed_by"] == "QAResponseStrategy"
        assert enhanced["_metadata"]["context"]["user_id"] == "test_user"
        assert "timestamp" in enhanced["_metadata"]
    
    def test_enhance_response_with_defaults(self):
        """Test response enhancement with default values."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response = {
            "answer": "Test answer"
            # Missing optional fields
        }
        
        enhanced = strategy._enhance_response(response)
        
        assert enhanced["answer"] == "Test answer"
        assert enhanced["confidence"] == 0.5  # Default value
        assert enhanced["sources"] == []  # Default value
        assert enhanced["follow_up_questions"] == []  # Default value
    
    def test_create_fallback_response(self):
        """Test fallback response creation."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        raw_response = "Python is a programming language used for web development and data science."
        context = {"topic": "programming"}
        
        fallback = strategy._create_fallback_response(raw_response, context)
        
        assert "answer" in fallback
        assert "confidence" in fallback
        assert fallback["confidence"] == 0.3
        assert fallback["_metadata"]["fallback_used"] is True
        assert fallback["_metadata"]["context"]["topic"] == "programming"
        assert "python" in fallback["tags"]
    
    def test_process_response_empty_response(self):
        """Test processing empty response."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        with pytest.raises(Exception, match="Response cannot be empty"):
            strategy.process_response("")
        
        with pytest.raises(Exception, match="Response cannot be empty"):
            strategy.process_response("   ")
    
    def test_process_response_with_context(self):
        """Test processing response with context."""
        strategy = QAResponseStrategy(schema_path=self.schema_file)
        
        response_data = {
            "answer": "Context-aware answer",
            "confidence": 0.9
        }
        
        context = {"user_level": "beginner", "topic": "programming"}
        processed = strategy.process_response(json.dumps(response_data), context)
        
        assert processed["answer"] == "Context-aware answer"
        assert processed["_metadata"]["context"]["user_level"] == "beginner"
        assert processed["_metadata"]["context"]["topic"] == "programming"
