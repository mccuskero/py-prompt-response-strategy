#!/usr/bin/env python3
"""
Question-Answer Prompt Strategy for SampleStrategyPipeline.

This strategy loads the question-answer JSON schema and creates conversational
prompts with context, history, and structured formatting.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from prompt_xml_strategies.prompt_strategies.interface import PromptCreationStrategy


class QAPromptStrategy(PromptCreationStrategy):
    """Prompt strategy that uses the question-answer schema to generate conversational prompts."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize the strategy with a schema file path.
        
        Args:
            schema_path: Path to the JSON schema file. If None, uses default.
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
        return str(project_root / "prompt_xml_strategies" / "schemas" / "prompts" / "sample" / "question_answer.json")
    
    def _load_schema(self) -> None:
        """Load the schema from the JSON file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")
    
    def create_prompt(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Create a conversational prompt using the loaded question-answer schema.
        
        Args:
            input_data: Input data containing question, context, and conversation history
            context: Optional context information
            
        Returns:
            Generated conversational prompt string
        """
        if not self.schema_data:
            raise ValueError("Schema not loaded")
        
        # Extract data from input_data
        question = input_data.get('question') or input_data.get('user_input', '')
        system_message = input_data.get('system_message', '')
        conversation_history = input_data.get('conversation_history', [])
        additional_context = input_data.get('additional_context', '')
        user_name = input_data.get('user_name', 'User')
        assistant_name = input_data.get('assistant_name', 'Assistant')
        
        # Build the prompt
        prompt_parts = []
        
        # System message (if provided)
        if system_message:
            prompt_parts.append(f"System: {system_message}")
            prompt_parts.append("")
        
        # Additional context (if provided)
        if additional_context:
            prompt_parts.append(f"Context: {additional_context}")
            prompt_parts.append("")
        
        # Conversation history
        if conversation_history:
            prompt_parts.append("Conversation History:")
            for message in conversation_history:
                role = message.get('role', 'user')
                content = message.get('content', '')
                timestamp = message.get('timestamp', '')
                
                # Format role names
                if role == 'user':
                    role_display = user_name
                elif role == 'assistant':
                    role_display = assistant_name
                else:
                    role_display = role.title()
                
                # Add timestamp if available
                time_str = f" ({timestamp})" if timestamp else ""
                prompt_parts.append(f"{role_display}{time_str}: {content}")
            
            prompt_parts.append("")
        
        # Current question
        if question:
            prompt_parts.append(f"{user_name}: {question}")
            prompt_parts.append("")
        
        # Instructions for the assistant
        prompt_parts.append(f"Please provide a helpful and accurate response to the question above. If you need clarification or additional information, please ask for it.")
        prompt_parts.append("")
        prompt_parts.append("Response format:")
        prompt_parts.append("- Be clear and concise")
        prompt_parts.append("- Provide specific examples when helpful")
        prompt_parts.append("- If you're uncertain about something, say so")
        prompt_parts.append("- Maintain a helpful and professional tone")
        
        # Add context information if available
        if context:
            prompt_parts.append("")
            prompt_parts.append("Additional Context:")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
        
        return "\n".join(prompt_parts)
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": "QAPromptStrategy",
            "version": "1.0.0",
            "description": "Generates conversational prompts using question-answer schema",
            "schema_path": self.schema_path,
            "schema_loaded": self.schema_data is not None,
            "schema_title": self.schema_data.get('title') if self.schema_data else None,
            "schema_id": self.schema_data.get('$id') if self.schema_data else None
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for this strategy.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(input_data, dict):
            return False
        
        # Check for at least one required field
        required_fields = ['question', 'user_input', 'conversation_history']
        has_required = any(field in input_data for field in required_fields)
        
        if not has_required:
            return False
        
        # Validate question/user_input if present
        if 'question' in input_data and not isinstance(input_data['question'], str):
            return False
        if 'user_input' in input_data and not isinstance(input_data['user_input'], str):
            return False
        
        # Validate conversation_history if present
        if 'conversation_history' in input_data:
            history = input_data['conversation_history']
            if not isinstance(history, list):
                return False
            
            for message in history:
                if not isinstance(message, dict):
                    return False
                if 'role' not in message or 'content' not in message:
                    return False
                if message['role'] not in ['user', 'assistant', 'system']:
                    return False
        
        return True
    
    def get_template_variables(self) -> List[str]:
        """Get available template variables for this strategy.
        
        Returns:
            List of variable names
        """
        return [
            'question',
            'user_input',
            'system_message',
            'conversation_history',
            'additional_context',
            'user_name',
            'assistant_name'
        ]
    
    def reload_schema(self, schema_path: Optional[str] = None) -> None:
        """Reload the schema from file.
        
        Args:
            schema_path: Optional new schema path. If None, reloads current.
        """
        if schema_path:
            self.schema_path = schema_path
        self._load_schema()
    
    def get_schema_properties(self) -> Dict[str, Any]:
        """Get the properties from the loaded schema.
        
        Returns:
            Dictionary with schema properties
        """
        if not self.schema_data:
            return {}
        return self.schema_data.get('properties', {})
    
    def get_schema_requirements(self) -> List[List[str]]:
        """Get the anyOf requirements from the loaded schema.
        
        Returns:
            List of requirement lists
        """
        if not self.schema_data:
            return []
        return self.schema_data.get('anyOf', [])
