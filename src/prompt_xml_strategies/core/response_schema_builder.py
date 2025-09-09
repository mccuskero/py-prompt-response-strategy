"""Build response format instructions for inclusion in prompts."""

import json
from typing import Any, Dict, List, Optional


class ResponseSchemaBuilder:
    """Builds response format instructions for inclusion in prompts."""
    
    def build_format_instructions(
        self, 
        response_schema: Dict[str, Any],
        instruction_style: str = "detailed"
    ) -> str:
        """Build format instructions from response schema.
        
        Args:
            response_schema: The JSON schema for expected response
            instruction_style: Style of instructions ("detailed", "concise", "example")
            
        Returns:
            Formatted instruction string
        """
        if instruction_style == "detailed":
            return self._build_detailed_instructions(response_schema)
        elif instruction_style == "concise":
            return self._build_concise_instructions(response_schema)
        elif instruction_style == "example":
            return self._build_example_instructions(response_schema)
        else:
            raise ValueError(f"Unknown instruction style: {instruction_style}")
    
    def _build_detailed_instructions(self, schema: Dict[str, Any]) -> str:
        """Build detailed format instructions.
        
        Args:
            schema: The response schema
            
        Returns:
            Detailed instruction string
        """
        instructions = ["Please provide your response in the following JSON format:"]
        
        # Add schema description if available
        if "description" in schema:
            instructions.append(f"\n{schema['description']}")
        
        instructions.append("\n```json")
        instructions.append(json.dumps(self._generate_example_from_schema(schema), indent=2))
        instructions.append("```")
        
        # Add field descriptions
        if "properties" in schema:
            instructions.append("\nField descriptions:")
            for field_name, field_schema in schema["properties"].items():
                if isinstance(field_schema, dict) and "description" in field_schema:
                    instructions.append(f"- {field_name}: {field_schema['description']}")
        
        # Add required fields info
        if "required" in schema:
            required_fields = schema["required"]
            instructions.append(f"\nRequired fields: {', '.join(required_fields)}")
        
        instructions.append("\nEnsure your response is valid JSON that matches this structure exactly.")
        
        return "\n".join(instructions)
    
    def _build_concise_instructions(self, schema: Dict[str, Any]) -> str:
        """Build concise format instructions.
        
        Args:
            schema: The response schema
            
        Returns:
            Concise instruction string
        """
        example = self._generate_example_from_schema(schema)
        return f"Respond in JSON format: {json.dumps(example)}"
    
    def _build_example_instructions(self, schema: Dict[str, Any]) -> str:
        """Build example-based format instructions.
        
        Args:
            schema: The response schema
            
        Returns:
            Example instruction string
        """
        example = self._generate_example_from_schema(schema)
        return f"Response format:\n```json\n{json.dumps(example, indent=2)}\n```"
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example data from JSON schema.
        
        Args:
            schema: The JSON schema
            
        Returns:
            Example data matching the schema
        """
        if "type" not in schema:
            return {}
        
        if schema["type"] == "object":
            return self._generate_object_example(schema)
        elif schema["type"] == "array":
            return self._generate_array_example(schema)
        else:
            return self._generate_primitive_example(schema)
    
    def _generate_object_example(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example object from schema.
        
        Args:
            schema: Object schema
            
        Returns:
            Example object
        """
        example = {}
        
        if "properties" not in schema:
            return example
        
        for prop_name, prop_schema in schema["properties"].items():
            if isinstance(prop_schema, dict):
                example[prop_name] = self._generate_example_from_schema(prop_schema)
            else:
                example[prop_name] = f"<{prop_name}>"
        
        return example
    
    def _generate_array_example(self, schema: Dict[str, Any]) -> List[Any]:
        """Generate example array from schema.
        
        Args:
            schema: Array schema
            
        Returns:
            Example array
        """
        if "items" not in schema:
            return ["<item>"]
        
        item_schema = schema["items"]
        example_item = self._generate_example_from_schema(item_schema)
        
        # Return array with one or two example items
        return [example_item]
    
    def _generate_primitive_example(self, schema: Dict[str, Any]) -> Any:
        """Generate example primitive value from schema.
        
        Args:
            schema: Primitive schema
            
        Returns:
            Example primitive value
        """
        schema_type = schema.get("type", "string")
        
        # Check for examples in schema
        if "examples" in schema and schema["examples"]:
            return schema["examples"][0]
        
        if "example" in schema:
            return schema["example"]
        
        # Generate default examples by type
        type_examples = {
            "string": "example_string",
            "integer": 42,
            "number": 42.0,
            "boolean": True,
            "null": None,
        }
        
        return type_examples.get(schema_type, "example_value")
    
    def get_required_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Extract required fields from schema.
        
        Args:
            schema: The JSON schema
            
        Returns:
            List of required field names
        """
        return schema.get("required", [])
    
    def get_field_descriptions(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Extract field descriptions from schema.
        
        Args:
            schema: The JSON schema
            
        Returns:
            Dictionary mapping field names to descriptions
        """
        descriptions = {}
        
        if "properties" in schema:
            for field_name, field_schema in schema["properties"].items():
                if isinstance(field_schema, dict) and "description" in field_schema:
                    descriptions[field_name] = field_schema["description"]
        
        return descriptions