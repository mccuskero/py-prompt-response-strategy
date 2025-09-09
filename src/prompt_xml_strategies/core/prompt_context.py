"""Context object containing data and configuration for prompt generation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, validator


class PromptContext(BaseModel):
    """Context object containing data and configuration for prompt generation."""
    
    data: Dict[str, Any] = Field(..., description="Input data for prompt generation")
    prompt_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for prompt validation")
    response_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for response validation") 
    xsd_schema: Optional[Union[str, Path]] = Field(None, description="XSD schema path for XML transformation")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    template_name: Optional[str] = Field(None, description="Custom template name")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        
    @validator('xsd_schema')
    def validate_xsd_schema(cls, v: Optional[Union[str, Path]]) -> Optional[Path]:
        """Validate XSD schema path."""
        if v is None:
            return v
        
        path = Path(v) if isinstance(v, str) else v
        if not path.exists():
            raise ValueError(f"XSD schema file not found: {path}")
        if path.suffix.lower() != '.xsd':
            raise ValueError(f"XSD schema file must have .xsd extension: {path}")
        
        return path
    
    @validator('data')
    def validate_data_not_empty(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that data is not empty."""
        if not v:
            raise ValueError("Data cannot be empty")
        return v
    
    def has_prompt_schema(self) -> bool:
        """Check if prompt schema is provided."""
        return self.prompt_schema is not None
    
    def has_response_schema(self) -> bool:
        """Check if response schema is provided."""
        return self.response_schema is not None
    
    def has_xsd_schema(self) -> bool:
        """Check if XSD schema is provided."""
        return self.xsd_schema is not None
    
    def get_data_field(self, field_name: str, default: Any = None) -> Any:
        """Get a specific field from data.
        
        Args:
            field_name: The field name to retrieve
            default: Default value if field not found
            
        Returns:
            The field value or default
        """
        return self.data.get(field_name, default)
    
    def set_data_field(self, field_name: str, value: Any) -> None:
        """Set a specific field in data.
        
        Args:
            field_name: The field name to set
            value: The value to set
        """
        self.data[field_name] = value
    
    def get_metadata_field(self, field_name: str, default: Any = None) -> Any:
        """Get a specific field from metadata.
        
        Args:
            field_name: The field name to retrieve
            default: Default value if field not found
            
        Returns:
            The field value or default
        """
        if not self.metadata:
            return default
        return self.metadata.get(field_name, default)
    
    def set_metadata_field(self, field_name: str, value: Any) -> None:
        """Set a specific field in metadata.
        
        Args:
            field_name: The field name to set
            value: The value to set
        """
        if not self.metadata:
            self.metadata = {}
        self.metadata[field_name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "data": self.data,
            "metadata": self.metadata or {},
        }
        
        if self.prompt_schema:
            result["prompt_schema"] = self.prompt_schema
        if self.response_schema:
            result["response_schema"] = self.response_schema
        if self.xsd_schema:
            result["xsd_schema"] = str(self.xsd_schema)
        if self.template_name:
            result["template_name"] = self.template_name
            
        return result