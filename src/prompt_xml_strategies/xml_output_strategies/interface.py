"""Interface for XML output strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from xml.etree.ElementTree import Element


class XmlOutputStrategy(ABC):
    """Abstract interface for XML output strategies."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def validate_xml(self, xml_element: Element) -> bool:
        """Validate XML against XSD schema.
        
        Args:
            xml_element: XML element to validate
            
        Returns:
            True if XML is valid
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        pass