"""Simple XML output strategy implementation."""

from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element, SubElement
import datetime

from .interface import XmlOutputStrategy
from ..core.exceptions import ValidationError


class SimpleXmlOutputStrategy(XmlOutputStrategy):
    """Simple implementation of XML output strategy."""
    
    def __init__(self):
        """Initialize the simple XML strategy."""
        self.root_element_name = "response"
    
    def transform_to_xml(
        self,
        response_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Element:
        """Transform response data to XML element.
        
        Args:
            response_data: Structured response data
            context: Optional context information
            
        Returns:
            XML Element tree
            
        Raises:
            ValidationError: If transformation fails
        """
        if not isinstance(response_data, dict):
            raise ValidationError("Response data must be a dictionary")
        
        try:
            # Create root element
            root = Element(self.root_element_name)
            
            # Add timestamp
            root.set("timestamp", datetime.datetime.utcnow().isoformat())
            
            # Add context as attributes if provided
            if context:
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        root.set(f"context_{key}", str(value))
            
            # Transform response data recursively
            self._dict_to_xml(response_data, root)
            
            if self.validate_xml(root):
                return root
                
        except Exception as e:
            raise ValidationError(f"Failed to transform data to XML: {str(e)}")
    
    def _dict_to_xml(self, data: Dict[str, Any], parent: Element) -> None:
        """Recursively convert dictionary to XML elements.
        
        Args:
            data: Dictionary data to convert
            parent: Parent XML element
        """
        for key, value in data.items():
            # Clean key name for XML element
            clean_key = self._clean_element_name(key)
            
            if isinstance(value, dict):
                # Create nested element for dictionary
                child = SubElement(parent, clean_key)
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                # Create multiple elements for list items
                for i, item in enumerate(value):
                    child = SubElement(parent, clean_key)
                    child.set("index", str(i))
                    if isinstance(item, dict):
                        self._dict_to_xml(item, child)
                    else:
                        child.text = str(item)
            else:
                # Create simple element for primitive values
                child = SubElement(parent, clean_key)
                child.text = str(value) if value is not None else ""
    
    def _clean_element_name(self, name: str) -> str:
        """Clean element name to be valid XML.
        
        Args:
            name: Original element name
            
        Returns:
            Cleaned element name
        """
        # Replace invalid characters with underscores
        import re
        cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', str(name))
        
        # Ensure it starts with a letter or underscore
        if cleaned and not cleaned[0].isalpha() and cleaned[0] != '_':
            cleaned = '_' + cleaned
        
        return cleaned or 'element'
    
    def validate_xml(self, xml_element: Element) -> bool:
        """Validate XML against basic requirements.
        
        Args:
            xml_element: XML element to validate
            
        Returns:
            True if XML is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if xml_element is None:
            raise ValidationError("XML element cannot be None")
        
        if not xml_element.tag:
            raise ValidationError("XML element must have a tag")
        
        # Basic validation - element exists and has a valid tag
        return True
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": "SimpleXmlOutputStrategy",
            "description": "Basic XML output generation from structured data",
            "supports_nested_data": True,
            "supports_arrays": True,
            "root_element": self.root_element_name,
            "version": "1.0.0"
        }