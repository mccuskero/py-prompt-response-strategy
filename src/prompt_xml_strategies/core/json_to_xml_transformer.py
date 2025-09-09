"""JSON to XML transformation using XSD schemas."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import xmlschema
from lxml import etree

from .schema_validator import SchemaValidator, ValidationError


class TransformationError(Exception):
    """Exception raised during JSON to XML transformation."""
    pass


class JSONToXMLTransformer:
    """Transforms validated JSON responses into XML documents."""
    
    def __init__(self, validator: Optional[SchemaValidator] = None) -> None:
        """Initialize the transformer.
        
        Args:
            validator: Optional schema validator instance
        """
        self.validator = validator or SchemaValidator()
    
    def transform(
        self, 
        json_data: Dict[str, Any], 
        xsd_schema_path: Union[str, Path],
        root_element_name: Optional[str] = None
    ) -> etree.Element:
        """Transform JSON data to XML using XSD schema structure.
        
        Args:
            json_data: The JSON data to transform
            xsd_schema_path: Path to the XSD schema file
            root_element_name: Optional custom root element name
            
        Returns:
            The XML element tree
            
        Raises:
            TransformationError: If transformation fails
            ValidationError: If validation fails
        """
        try:
            # Load XSD schema
            xsd_schema = self.validator.load_xsd_schema(xsd_schema_path)
            
            # Determine root element name
            if root_element_name is None:
                root_element_name = self._get_root_element_name(xsd_schema)
            
            # Create root element
            root = etree.Element(root_element_name)
            
            # Transform JSON data to XML elements
            self._transform_object_to_element(json_data, root, xsd_schema)
            
            # Validate the generated XML
            self.validator.validate_xml_against_xsd(root, xsd_schema_path)
            
            return root
            
        except Exception as e:
            if isinstance(e, (ValidationError, TransformationError)):
                raise
            raise TransformationError(f"Unexpected error during transformation: {str(e)}")
    
    def transform_to_string(
        self, 
        json_data: Dict[str, Any], 
        xsd_schema_path: Union[str, Path],
        root_element_name: Optional[str] = None,
        pretty_print: bool = True,
        encoding: str = "utf-8"
    ) -> str:
        """Transform JSON data to XML string.
        
        Args:
            json_data: The JSON data to transform
            xsd_schema_path: Path to the XSD schema file
            root_element_name: Optional custom root element name
            pretty_print: Whether to format XML with indentation
            encoding: XML encoding
            
        Returns:
            The XML string
            
        Raises:
            TransformationError: If transformation fails
        """
        xml_element = self.transform(json_data, xsd_schema_path, root_element_name)
        
        return etree.tostring(
            xml_element, 
            pretty_print=pretty_print, 
            encoding=encoding,
            xml_declaration=True
        ).decode(encoding)
    
    def transform_to_file(
        self,
        json_data: Dict[str, Any],
        xsd_schema_path: Union[str, Path],
        output_file: Union[str, Path],
        root_element_name: Optional[str] = None,
        pretty_print: bool = True,
        encoding: str = "utf-8"
    ) -> None:
        """Transform JSON data to XML file.
        
        Args:
            json_data: The JSON data to transform
            xsd_schema_path: Path to the XSD schema file
            output_file: Path to the output XML file
            root_element_name: Optional custom root element name
            pretty_print: Whether to format XML with indentation
            encoding: XML encoding
            
        Raises:
            TransformationError: If transformation fails
        """
        xml_element = self.transform(json_data, xsd_schema_path, root_element_name)
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(etree.tostring(
                xml_element,
                pretty_print=pretty_print,
                encoding=encoding,
                xml_declaration=True
            ))
    
    def _get_root_element_name(self, xsd_schema: xmlschema.XMLSchema) -> str:
        """Get the root element name from XSD schema.
        
        Args:
            xsd_schema: The XSD schema
            
        Returns:
            The root element name
            
        Raises:
            TransformationError: If root element cannot be determined
        """
        # Get the first global element as root
        global_elements = list(xsd_schema.elements.keys())
        if not global_elements:
            raise TransformationError("No global elements found in XSD schema")
        
        return global_elements[0]
    
    def _transform_object_to_element(
        self, 
        data: Dict[str, Any], 
        parent: etree.Element, 
        xsd_schema: xmlschema.XMLSchema
    ) -> None:
        """Transform a JSON object to XML elements.
        
        Args:
            data: The JSON object data
            parent: The parent XML element
            xsd_schema: The XSD schema
        """
        for key, value in data.items():
            if isinstance(value, dict):
                # Create child element for nested object
                child = etree.SubElement(parent, key)
                self._transform_object_to_element(value, child, xsd_schema)
            elif isinstance(value, list):
                # Handle arrays
                self._transform_array_to_elements(key, value, parent, xsd_schema)
            else:
                # Handle primitive values
                self._transform_value_to_element(key, value, parent, xsd_schema)
    
    def _transform_array_to_elements(
        self, 
        key: str, 
        array: list, 
        parent: etree.Element, 
        xsd_schema: xmlschema.XMLSchema
    ) -> None:
        """Transform a JSON array to XML elements.
        
        Args:
            key: The element name
            array: The array data
            parent: The parent XML element
            xsd_schema: The XSD schema
        """
        for item in array:
            if isinstance(item, dict):
                child = etree.SubElement(parent, key)
                self._transform_object_to_element(item, child, xsd_schema)
            else:
                self._transform_value_to_element(key, item, parent, xsd_schema)
    
    def _transform_value_to_element(
        self, 
        key: str, 
        value: Any, 
        parent: etree.Element, 
        xsd_schema: xmlschema.XMLSchema
    ) -> None:
        """Transform a primitive value to XML element.
        
        Args:
            key: The element name
            value: The value
            parent: The parent XML element
            xsd_schema: The XSD schema
        """
        # Check if this should be an attribute based on XSD schema
        if self._should_be_attribute(key, parent.tag, xsd_schema):
            parent.set(key, str(value))
        else:
            child = etree.SubElement(parent, key)
            child.text = str(value) if value is not None else ""
    
    def _should_be_attribute(
        self, 
        name: str, 
        parent_name: str, 
        xsd_schema: xmlschema.XMLSchema
    ) -> bool:
        """Check if a field should be an XML attribute based on XSD schema.
        
        Args:
            name: The field name
            parent_name: The parent element name
            xsd_schema: The XSD schema
            
        Returns:
            True if field should be an attribute
        """
        try:
            # Try to find the element definition in the schema
            if parent_name in xsd_schema.elements:
                element_def = xsd_schema.elements[parent_name]
                if hasattr(element_def, 'type') and hasattr(element_def.type, 'attributes'):
                    return name in element_def.type.attributes
            return False
        except Exception:
            # If we can't determine, default to element
            return False