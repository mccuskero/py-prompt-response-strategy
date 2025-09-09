"""XML document construction utilities."""

from typing import Any, Dict
from lxml import etree


class XMLBuilder:
    """Constructs XML elements from JSON data based on XSD structure."""
    
    def __init__(self) -> None:
        """Initialize the XML builder."""
        pass
    
    def build_element(
        self, 
        name: str, 
        data: Any,
        parent: etree.Element = None
    ) -> etree.Element:
        """Build XML element from data.
        
        Args:
            name: Element name
            data: Data to convert
            parent: Parent element
            
        Returns:
            Created XML element
        """
        if parent is not None:
            element = etree.SubElement(parent, name)
        else:
            element = etree.Element(name)
        
        if isinstance(data, dict):
            for key, value in data.items():
                self.build_element(key, value, element)
        elif isinstance(data, list):
            for item in data:
                # For lists, create multiple child elements with same name
                item_name = name.rstrip('s')  # Simple singularization
                self.build_element(item_name, item, element)
        else:
            # Scalar value
            element.text = str(data) if data is not None else ""
        
        return element
    
    def build_document(
        self, 
        root_name: str, 
        data: Dict[str, Any],
        encoding: str = "utf-8"
    ) -> etree.ElementTree:
        """Build complete XML document.
        
        Args:
            root_name: Name of root element
            data: Data to convert
            encoding: Document encoding
            
        Returns:
            XML document tree
        """
        root = self.build_element(root_name, data)
        return etree.ElementTree(root)