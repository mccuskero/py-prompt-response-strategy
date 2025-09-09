"""XSD schema validation for XML documents."""

from pathlib import Path
from typing import Union

import xmlschema
from lxml import etree

from .schema_validator import ValidationError


class XSDValidator:
    """Validates XML documents against XSD schemas."""
    
    def __init__(self) -> None:
        """Initialize the XSD validator."""
        self._schemas = {}
    
    def validate(
        self, 
        xml_content: Union[str, bytes, etree.Element], 
        xsd_path: Union[str, Path]
    ) -> bool:
        """Validate XML content against XSD schema.
        
        Args:
            xml_content: The XML content to validate
            xsd_path: Path to the XSD schema file
            
        Returns:
            True if XML is valid
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Load schema
            schema_path = str(Path(xsd_path).absolute())
            if schema_path not in self._schemas:
                self._schemas[schema_path] = xmlschema.XMLSchema(schema_path)
            
            schema = self._schemas[schema_path]
            
            # Parse XML if needed
            if isinstance(xml_content, (str, bytes)):
                if isinstance(xml_content, str):
                    xml_content = xml_content.encode('utf-8')
                xml_doc = etree.fromstring(xml_content)
            else:
                xml_doc = xml_content
            
            # Validate
            schema.validate(xml_doc)
            return True
            
        except xmlschema.XMLSchemaException as e:
            raise ValidationError(f"XSD validation failed: {str(e)}")
        except etree.XMLSyntaxError as e:
            raise ValidationError(f"XML parsing error: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Unexpected error during XSD validation: {str(e)}")