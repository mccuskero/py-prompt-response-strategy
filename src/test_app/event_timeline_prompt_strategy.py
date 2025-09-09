#!/usr/bin/env python3
"""
Event Timeline Prompt Strategy for SampleStrategyPipeline.

This strategy loads event timeline schemas and creates structured prompts
for analyzing temporal event sequences.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from prompt_xml_strategies.prompt_strategies.interface import PromptCreationStrategy


class EventTimelinePromptStrategy(PromptCreationStrategy):
    """Prompt strategy that uses event timeline schemas to generate structured prompts."""
    
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
        return str(current_dir / "schemas" / "prompts" / "event_timeline_prompt_schema.json")
    
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
        """Create a prompt using the loaded event timeline schema.
        
        Args:
            input_data: Input data containing analysis requirements
            context: Optional context information
            
        Returns:
            Generated prompt string
        """
        if not self.schema_data:
            raise ValueError("Schema not loaded")
        
        # Extract analysis requirements from input data
        analysis_type = input_data.get('analysis_type', 'general')
        focus_areas = input_data.get('focus_areas', [])
        output_format = input_data.get('output_format', 'structured')
        
        # Build the prompt using the schema
        prompt_parts = []
        
        # Header
        prompt_parts.append(f"# {self.schema_data['name']}")
        prompt_parts.append(f"## {self.schema_data['description']}")
        prompt_parts.append("")
        
        # Event timeline section
        prompt_parts.append("## Event Timeline")
        prompt_parts.append("Analyze the following sequence of events and provide insights:")
        prompt_parts.append("")
        
        for event in self.schema_data['event_list']:
            prompt_parts.append(f"**{event['id']}** ({event['relative_time']}): {event['action']}")
        
        prompt_parts.append("")
        
        # Analysis requirements
        prompt_parts.append("## Analysis Requirements")
        prompt_parts.append(f"**Analysis Type:** {analysis_type}")
        
        if focus_areas:
            prompt_parts.append(f"**Focus Areas:** {', '.join(focus_areas)}")
        
        prompt_parts.append(f"**Output Format:** {output_format}")
        prompt_parts.append("")
        
        # Schema metadata
        events_info = self.schema_data['events']
        prompt_parts.append("## Timeline Metadata")
        prompt_parts.append(f"- **Total Events:** {events_info['total_count']}")
        prompt_parts.append(f"- **Time Span:** {events_info['time_span']}")
        prompt_parts.append(f"- **Categories:** {', '.join(events_info['categories'].keys())}")
        prompt_parts.append("")
        
        # Analysis instructions
        prompt_parts.append("## Analysis Instructions")
        prompt_parts.append("Please provide a comprehensive analysis that includes:")
        prompt_parts.append("1. **Temporal Analysis:** Identify patterns, sequences, and timing relationships")
        prompt_parts.append("2. **Critical Path Analysis:** Highlight the most important events for system startup")
        prompt_parts.append("3. **Parallel Processing:** Identify events that occur simultaneously")
        prompt_parts.append("4. **Performance Insights:** Analyze timing and identify potential bottlenecks")
        prompt_parts.append("5. **Dependencies:** Map out event dependencies and prerequisites")
        prompt_parts.append("")
        
        # Context information
        if context:
            prompt_parts.append("## Additional Context")
            for key, value in context.items():
                prompt_parts.append(f"- **{key}:** {value}")
            prompt_parts.append("")
        
        # Output format specification
        prompt_parts.append("## Expected Output Format")
        prompt_parts.append("Provide your analysis in the following JSON structure:")
        prompt_parts.append("```json")
        prompt_parts.append("{")
        prompt_parts.append('  "temporal_analysis": {')
        prompt_parts.append('    "total_duration": "HH:MM:SS",')
        prompt_parts.append('    "average_event_interval": "seconds",')
        prompt_parts.append('    "longest_gap": "seconds",')
        prompt_parts.append('    "shortest_gap": "seconds"')
        prompt_parts.append('  },')
        prompt_parts.append('  "critical_path": [')
        prompt_parts.append('    "event_id_1", "event_id_2", ...')
        prompt_parts.append('  ],')
        prompt_parts.append('  "parallel_events": [')
        prompt_parts.append('    ["event_id_a", "event_id_b"], ...')
        prompt_parts.append('  ],')
        prompt_parts.append('  "performance_insights": {')
        prompt_parts.append('    "bottlenecks": ["event_id"],')
        prompt_parts.append('    "optimization_opportunities": ["suggestion"]')
        prompt_parts.append('  },')
        prompt_parts.append('  "dependencies": {')
        prompt_parts.append('    "event_id": ["prerequisite_event_ids"]')
        prompt_parts.append('  },')
        prompt_parts.append('  "summary": "Overall analysis summary"')
        prompt_parts.append("}")
        prompt_parts.append("```")
        
        return "\n".join(prompt_parts)
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": "EventTimelinePromptStrategy",
            "version": "1.0.0",
            "description": "Generates prompts for event timeline analysis using JSON schemas",
            "schema_path": self.schema_path,
            "schema_loaded": self.schema_data is not None,
            "schema_name": self.schema_data.get('name') if self.schema_data else None
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
        
        # Check for required fields
        required_fields = ['analysis_type']
        for field in required_fields:
            if field not in input_data:
                return False
        
        # Validate analysis_type
        valid_types = ['general', 'performance', 'dependency', 'temporal', 'critical_path']
        if input_data.get('analysis_type') not in valid_types:
            return False
        
        return True
    
    def get_template_variables(self) -> List[str]:
        """Get available template variables for this strategy.
        
        Returns:
            List of variable names
        """
        return [
            'analysis_type',
            'focus_areas',
            'output_format',
            'schema_name',
            'event_count',
            'time_span'
        ]
    
    def reload_schema(self, schema_path: Optional[str] = None) -> None:
        """Reload the schema from file.
        
        Args:
            schema_path: Optional new schema path. If None, reloads current.
        """
        if schema_path:
            self.schema_path = schema_path
        self._load_schema()
    
    def get_schema_events(self) -> List[Dict[str, Any]]:
        """Get the event list from the loaded schema.
        
        Returns:
            List of event dictionaries
        """
        if not self.schema_data:
            return []
        return self.schema_data.get('event_list', [])
    
    def get_schema_metadata(self) -> Dict[str, Any]:
        """Get the events metadata from the loaded schema.
        
        Returns:
            Dictionary with events metadata
        """
        if not self.schema_data:
            return {}
        return self.schema_data.get('events', {})
