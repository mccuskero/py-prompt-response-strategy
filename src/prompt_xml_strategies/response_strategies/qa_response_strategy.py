"""Question-Answer response creation strategy implementation."""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from .interface import ResponseCreationStrategy
from ..core.exceptions import ValidationError


class QAResponseStrategy(ResponseCreationStrategy):
    """Response strategy for processing Q&A responses using JSON schema validation."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize the Q&A response strategy.
        
        Args:
            schema_path: Path to the Q&A response schema JSON file
        """
        super().__init__()
        self.schema_path = schema_path or self._get_default_schema_path()
        self.schema_data = None
        self._load_schema()
    
    def _get_default_schema_path(self) -> str:
        """Get the default schema path relative to this file."""
        current_dir = Path(__file__).parent
        # Go up to the project root to access the schemas
        project_root = current_dir.parent.parent
        return str(project_root / "prompt_xml_strategies" / "schemas" / "responses" / "sample" / "qa_response.json")
    
    def _load_schema(self) -> None:
        """Load the schema from the JSON file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {str(e)}")
    
    def process_response(
        self,
        raw_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process raw LLM response into structured Q&A data.
        
        Args:
            raw_response: Raw response from LLM
            context: Optional context information
            
        Returns:
            Structured Q&A response data
            
        Raises:
            ValidationError: If response processing fails
        """
        if not raw_response or not raw_response.strip():
            raise ValidationError("Response cannot be empty")
        
        # Try to extract JSON from code blocks first
        json_pattern = re.compile(r'```json\s*\n(.*?)\n```', re.DOTALL)
        json_match = json_pattern.search(raw_response)
        
        if json_match:
            json_str = json_match.group(1)
            try:
                parsed_data = json.loads(json_str)
                if self.validate_response(parsed_data):
                    return self._enhance_response(parsed_data, context)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Failed to parse JSON from response: {str(e)}")
        
        # Try to parse the entire response as JSON
        try:
            parsed_data = json.loads(raw_response)
            if self.validate_response(parsed_data):
                return self._enhance_response(parsed_data, context)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a structured response from text
            return self._create_fallback_response(raw_response, context)
    
    def _enhance_response(
        self, 
        response: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhance the response with additional metadata and validation.
        
        Args:
            response: Parsed response data
            context: Optional context information
            
        Returns:
            Enhanced response data
        """
        enhanced = response.copy()
        
        # Add metadata
        enhanced["_metadata"] = {
            "processed_by": "QAResponseStrategy",
            "schema_version": self.schema_data.get("$id", "unknown"),
            "context": context or {},
            "timestamp": self._get_timestamp()
        }
        
        # Ensure required fields have default values if missing
        if "answer" not in enhanced:
            enhanced["answer"] = "No answer provided"
        
        if "confidence" not in enhanced:
            enhanced["confidence"] = 0.5
        
        if "sources" not in enhanced:
            enhanced["sources"] = []
        
        if "follow_up_questions" not in enhanced:
            enhanced["follow_up_questions"] = []
        
        return enhanced
    
    def _create_fallback_response(
        self, 
        raw_response: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a fallback structured response when JSON parsing fails.
        
        Args:
            raw_response: Raw response text
            context: Optional context information
            
        Returns:
            Structured Q&A response dictionary
        """
        # Extract potential answer from the text
        answer = self._extract_answer_from_text(raw_response)
        
        # Extract potential follow-up questions
        follow_up_questions = self._extract_follow_up_questions(raw_response)
        
        # Determine difficulty level based on content
        difficulty_level = self._assess_difficulty_level(raw_response)
        
        # Extract tags from content
        tags = self._extract_tags(raw_response)
        
        return {
            "answer": answer,
            "confidence": 0.3,  # Lower confidence for fallback
            "sources": [],
            "follow_up_questions": follow_up_questions,
            "explanation": raw_response.strip(),
            "examples": [],
            "difficulty_level": difficulty_level,
            "tags": tags,
            "_metadata": {
                "processed_by": "QAResponseStrategy",
                "fallback_used": True,
                "original_length": len(raw_response),
                "context": context or {},
                "timestamp": self._get_timestamp()
            }
        }
    
    def _extract_answer_from_text(self, text: str) -> str:
        """Extract a concise answer from the text.
        
        Args:
            text: Raw response text
            
        Returns:
            Extracted answer
        """
        # Look for common answer patterns
        lines = text.strip().split('\n')
        
        # Take the first substantial line as the answer
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not line.startswith(('Question:', 'Answer:', 'Q:', 'A:')):
                return line
        
        # If no good line found, return first 200 characters
        return text.strip()[:200] + ("..." if len(text.strip()) > 200 else "")
    
    def _extract_follow_up_questions(self, text: str) -> List[str]:
        """Extract potential follow-up questions from the text.
        
        Args:
            text: Raw response text
            
        Returns:
            List of follow-up questions
        """
        questions = []
        
        # Look for question patterns
        question_patterns = [
            r'What about (.+?)\?',
            r'How about (.+?)\?',
            r'Can you explain (.+?)\?',
            r'What if (.+?)\?',
            r'Why (.+?)\?',
            r'When (.+?)\?',
            r'Where (.+?)\?',
            r'Who (.+?)\?'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                question = f"What about {match}?" if not match.endswith('?') else match
                if question not in questions:
                    questions.append(question)
        
        return questions[:3]  # Limit to 3 questions
    
    def _assess_difficulty_level(self, text: str) -> str:
        """Assess the difficulty level of the response.
        
        Args:
            text: Raw response text
            
        Returns:
            Difficulty level: 'beginner', 'intermediate', or 'advanced'
        """
        text_lower = text.lower()
        
        # Advanced indicators
        advanced_terms = ['algorithm', 'implementation', 'architecture', 'optimization', 'complexity', 'framework']
        if any(term in text_lower for term in advanced_terms):
            return 'advanced'
        
        # Beginner indicators
        beginner_terms = ['simple', 'basic', 'easy', 'start', 'begin', 'introduction']
        if any(term in text_lower for term in beginner_terms):
            return 'beginner'
        
        # Default to intermediate
        return 'intermediate'
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract topic tags from the text.
        
        Args:
            text: Raw response text
            
        Returns:
            List of topic tags
        """
        # Common technology and topic tags
        common_tags = [
            'python', 'javascript', 'java', 'c++', 'programming', 'coding',
            'ai', 'machine learning', 'data science', 'web development',
            'database', 'api', 'security', 'testing', 'deployment'
        ]
        
        text_lower = text.lower()
        found_tags = []
        
        for tag in common_tags:
            if tag in text_lower:
                found_tags.append(tag)
        
        return found_tags[:5]  # Limit to 5 tags
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate processed response against Q&A schema.
        
        Args:
            response: Processed response data
            
        Returns:
            True if response is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(response, dict):
            raise ValidationError("Response must be a dictionary")
        
        # Check required fields
        if "answer" not in response:
            raise ValidationError("Response must contain an 'answer' field")
        
        if not isinstance(response["answer"], str) or not response["answer"].strip():
            raise ValidationError("Answer must be a non-empty string")
        
        # Validate confidence if present
        if "confidence" in response:
            confidence = response["confidence"]
            if not isinstance(confidence, (int, float)):
                raise ValidationError("Confidence must be a number")
            if not 0 <= confidence <= 1:
                raise ValidationError("Confidence must be between 0 and 1")
        
        # Validate sources if present
        if "sources" in response:
            sources = response["sources"]
            if not isinstance(sources, list):
                raise ValidationError("Sources must be a list")
            for source in sources:
                if not isinstance(source, dict):
                    raise ValidationError("Each source must be a dictionary")
                if "title" not in source:
                    raise ValidationError("Each source must have a 'title' field")
        
        # Validate follow_up_questions if present
        if "follow_up_questions" in response:
            questions = response["follow_up_questions"]
            if not isinstance(questions, list):
                raise ValidationError("Follow-up questions must be a list")
            for question in questions:
                if not isinstance(question, str) or not question.strip():
                    raise ValidationError("Each follow-up question must be a non-empty string")
        
        # Validate difficulty_level if present
        if "difficulty_level" in response:
            level = response["difficulty_level"]
            if level not in ["beginner", "intermediate", "advanced"]:
                raise ValidationError("Difficulty level must be 'beginner', 'intermediate', or 'advanced'")
        
        # Validate tags if present
        if "tags" in response:
            tags = response["tags"]
            if not isinstance(tags, list):
                raise ValidationError("Tags must be a list")
            for tag in tags:
                if not isinstance(tag, str) or not tag.strip():
                    raise ValidationError("Each tag must be a non-empty string")
        
        return True
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": "QAResponseStrategy",
            "version": "1.0.0",
            "description": "Processes Q&A responses using JSON schema validation",
            "schema_path": self.schema_path,
            "schema_loaded": self.schema_data is not None,
            "schema_title": self.schema_data.get("title", "Unknown") if self.schema_data else "Unknown",
            "schema_id": self.schema_data.get("$id", "Unknown") if self.schema_data else "Unknown",
            "supports_json": True,
            "supports_fallback": True,
            "supports_validation": True
        }
    
    def get_schema_properties(self) -> List[str]:
        """Get the properties defined in the schema.
        
        Returns:
            List of property names
        """
        if not self.schema_data:
            return []
        
        properties = self.schema_data.get("properties", {})
        return list(properties.keys())
    
    def get_schema_requirements(self) -> List[str]:
        """Get the required fields from the schema.
        
        Returns:
            List of required field names
        """
        if not self.schema_data:
            return []
        
        return self.schema_data.get("required", [])
    
    def reload_schema(self, schema_path: Optional[str] = None) -> None:
        """Reload the schema from file.
        
        Args:
            schema_path: Optional new schema path
        """
        if schema_path:
            self.schema_path = schema_path
        self._load_schema()
