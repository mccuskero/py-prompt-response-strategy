"""Q&A XML output strategy implementation using XSD schema validation."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List
from xml.etree.ElementTree import Element, SubElement
import datetime
import xmlschema

from .interface import XmlOutputStrategy
from ..core.exceptions import ValidationError


class QAXmlOutputStrategy(XmlOutputStrategy):
    """XML output strategy for Q&A responses using XSD schema validation."""
    
    def __init__(self, xsd_path: Optional[str] = None):
        """Initialize the Q&A XML strategy.
        
        Args:
            xsd_path: Path to the Q&A response XSD schema file
        """
        super().__init__()
        self.xsd_path = xsd_path or self._get_default_xsd_path()
        self.xsd_schema = None
        self.namespace = "https://prompt-xml-strategies.dev/schemas/xsd/conversational"
        self._load_xsd_schema()
    
    def _get_default_xsd_path(self) -> str:
        """Get the default XSD path relative to this file."""
        current_dir = Path(__file__).parent
        # Go up to the project root to access the schemas
        project_root = current_dir.parent.parent
        return str(project_root / "prompt_xml_strategies" / "schemas" / "xsd" / "conversational" / "qa_response.xsd")
    
    def _load_xsd_schema(self) -> None:
        """Load the XSD schema from file."""
        try:
            self.xsd_schema = xmlschema.XMLSchema(self.xsd_path)
        except (FileNotFoundError, xmlschema.exceptions.XMLResourceOSError) as e:
            if "No such file or directory" in str(e) or isinstance(e, FileNotFoundError):
                raise FileNotFoundError(f"XSD schema file not found: {self.xsd_path}")
            else:
                raise ValueError(f"Invalid XSD schema file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid XSD schema file: {str(e)}")
    
    def transform_to_xml(
        self,
        response_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Element:
        """Transform Q&A response data to XML element using XSD schema.
        
        Args:
            response_data: Structured Q&A response data
            context: Optional context information
            
        Returns:
            XML Element tree conforming to XSD schema
            
        Raises:
            ValidationError: If transformation fails
        """
        if not isinstance(response_data, dict):
            raise ValidationError("Response data must be a dictionary")
        
        try:
            # Create root element with namespace
            root = Element(f"{{{self.namespace}}}qa_response")
            root.set("xmlns", self.namespace)
            
            # Add context as attributes if provided
            if context:
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        root.set(f"context_{key}", str(value))
            
            # Required field: answer
            if "answer" not in response_data:
                raise ValidationError("Q&A response must contain an 'answer' field")
            
            answer_elem = SubElement(root, f"{{{self.namespace}}}answer")
            answer_elem.text = str(response_data["answer"])
            
            # Optional field: confidence
            if "confidence" in response_data:
                confidence_elem = SubElement(root, f"{{{self.namespace}}}confidence")
                confidence_value = response_data["confidence"]
                if not isinstance(confidence_value, (int, float)):
                    raise ValidationError("Confidence must be a number")
                if not 0 <= confidence_value <= 1:
                    raise ValidationError("Confidence must be between 0 and 1")
                confidence_elem.text = str(confidence_value)
            
            # Optional field: sources
            if "sources" in response_data and response_data["sources"]:
                sources_elem = SubElement(root, f"{{{self.namespace}}}sources")
                sources_data = response_data["sources"]
                
                if not isinstance(sources_data, list):
                    raise ValidationError("Sources must be a list")
                
                for source_data in sources_data:
                    if not isinstance(source_data, dict):
                        raise ValidationError("Each source must be a dictionary")
                    
                    source_elem = SubElement(sources_elem, f"{{{self.namespace}}}source")
                    
                    # Required field: title
                    if "title" not in source_data:
                        raise ValidationError("Each source must have a 'title' field")
                    title_elem = SubElement(source_elem, f"{{{self.namespace}}}title")
                    title_elem.text = str(source_data["title"])
                    
                    # Optional field: url
                    if "url" in source_data and source_data["url"]:
                        url_elem = SubElement(source_elem, f"{{{self.namespace}}}url")
                        url_elem.text = str(source_data["url"])
                    
                    # Optional field: type
                    if "type" in source_data and source_data["type"]:
                        type_elem = SubElement(source_elem, f"{{{self.namespace}}}type")
                        type_value = source_data["type"]
                        if type_value not in ["web", "book", "paper", "documentation"]:
                            raise ValidationError(f"Invalid source type: {type_value}")
                        type_elem.text = str(type_value)
            
            # Optional field: follow_up_questions
            if "follow_up_questions" in response_data and response_data["follow_up_questions"]:
                questions_elem = SubElement(root, f"{{{self.namespace}}}follow_up_questions")
                questions_data = response_data["follow_up_questions"]
                
                if not isinstance(questions_data, list):
                    raise ValidationError("Follow-up questions must be a list")
                
                for question in questions_data:
                    if not isinstance(question, str) or not question.strip():
                        raise ValidationError("Each follow-up question must be a non-empty string")
                    question_elem = SubElement(questions_elem, f"{{{self.namespace}}}question")
                    question_elem.text = str(question)
            
            # Optional field: explanation
            if "explanation" in response_data and response_data["explanation"]:
                explanation_elem = SubElement(root, f"{{{self.namespace}}}explanation")
                explanation_elem.text = str(response_data["explanation"])
            
            # Optional field: examples
            if "examples" in response_data and response_data["examples"]:
                examples_elem = SubElement(root, f"{{{self.namespace}}}examples")
                examples_data = response_data["examples"]
                
                if not isinstance(examples_data, list):
                    raise ValidationError("Examples must be a list")
                
                for example_data in examples_data:
                    if not isinstance(example_data, dict):
                        raise ValidationError("Each example must be a dictionary")
                    
                    example_elem = SubElement(examples_elem, f"{{{self.namespace}}}example")
                    
                    # Required field: description
                    if "description" not in example_data:
                        raise ValidationError("Each example must have a 'description' field")
                    desc_elem = SubElement(example_elem, f"{{{self.namespace}}}description")
                    desc_elem.text = str(example_data["description"])
                    
                    # Optional field: code
                    if "code" in example_data and example_data["code"]:
                        code_elem = SubElement(example_elem, f"{{{self.namespace}}}code")
                        code_elem.text = str(example_data["code"])
                    
                    # Optional field: output
                    if "output" in example_data and example_data["output"]:
                        output_elem = SubElement(example_elem, f"{{{self.namespace}}}output")
                        output_elem.text = str(example_data["output"])
            
            # Optional field: difficulty_level
            if "difficulty_level" in response_data and response_data["difficulty_level"]:
                difficulty_elem = SubElement(root, f"{{{self.namespace}}}difficulty_level")
                difficulty_value = response_data["difficulty_level"]
                if difficulty_value not in ["beginner", "intermediate", "advanced"]:
                    raise ValidationError(f"Invalid difficulty level: {difficulty_value}")
                difficulty_elem.text = str(difficulty_value)
            
            # Optional field: tags
            if "tags" in response_data and response_data["tags"]:
                tags_elem = SubElement(root, f"{{{self.namespace}}}tags")
                tags_data = response_data["tags"]
                
                if not isinstance(tags_data, list):
                    raise ValidationError("Tags must be a list")
                
                for tag in tags_data:
                    if not isinstance(tag, str) or not tag.strip():
                        raise ValidationError("Each tag must be a non-empty string")
                    tag_elem = SubElement(tags_elem, f"{{{self.namespace}}}tag")
                    tag_elem.text = str(tag)
            
            return root
            
        except Exception as e:
            raise ValidationError(f"XML transformation failed: {str(e)}") from e
    
    def validate_xml(self, xml_element: Element) -> bool:
        """Validate XML against Q&A XSD schema.
        
        Args:
            xml_element: XML element to validate
            
        Returns:
            True if XML is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not self.xsd_schema:
            raise ValidationError("XSD schema not loaded")
        
        try:
            # Convert Element to string for validation
            xml_string = ET.tostring(xml_element, encoding='unicode')
            
            # Validate against XSD schema
            self.xsd_schema.validate(xml_string)
            return True
            
        except Exception as e:
            raise ValidationError(f"XML validation failed: {str(e)}") from e
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "name": "QAXmlOutputStrategy",
            "version": "1.0.0",
            "description": "Generates Q&A XML output using XSD schema validation",
            "xsd_path": self.xsd_path,
            "xsd_loaded": self.xsd_schema is not None,
            "namespace": self.namespace,
            "supports_validation": True,
            "supports_namespaces": True
        }
    
    def get_xsd_info(self) -> Dict[str, Any]:
        """Get information about the loaded XSD schema.
        
        Returns:
            Dictionary with XSD schema information
        """
        if not self.xsd_schema:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "target_namespace": self.xsd_schema.target_namespace,
            "version": getattr(self.xsd_schema, 'version', 'Unknown'),
            "elements": list(self.xsd_schema.elements.keys()) if hasattr(self.xsd_schema, 'elements') else [],
            "types": list(self.xsd_schema.types.keys()) if hasattr(self.xsd_schema, 'types') else []
        }
    
    def reload_xsd(self, xsd_path: Optional[str] = None) -> None:
        """Reload the XSD schema from file.
        
        Args:
            xsd_path: Optional new XSD path
        """
        if xsd_path:
            self.xsd_path = xsd_path
        self._load_xsd_schema()
    
    def get_schema_elements(self) -> List[str]:
        """Get the elements defined in the XSD schema.
        
        Returns:
            List of element names
        """
        if not self.xsd_schema:
            return []
        
        try:
            return list(self.xsd_schema.elements.keys())
        except:
            return []
    
    def get_schema_types(self) -> List[str]:
        """Get the types defined in the XSD schema.
        
        Returns:
            List of type names
        """
        if not self.xsd_schema:
            return []
        
        try:
            return list(self.xsd_schema.types.keys())
        except:
            return []
    
    def validate_response_data(self, response_data: Dict[str, Any]) -> bool:
        """Validate response data before XML transformation.
        
        Args:
            response_data: Response data to validate
            
        Returns:
            True if data is valid for XML transformation
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(response_data, dict):
            raise ValidationError("Response data must be a dictionary")
        
        # Check required fields
        if "answer" not in response_data:
            raise ValidationError("Q&A response must contain an 'answer' field")
        
        if not isinstance(response_data["answer"], str) or not response_data["answer"].strip():
            raise ValidationError("Answer must be a non-empty string")
        
        # Validate confidence if present
        if "confidence" in response_data:
            confidence = response_data["confidence"]
            if not isinstance(confidence, (int, float)):
                raise ValidationError("Confidence must be a number")
            if not 0 <= confidence <= 1:
                raise ValidationError("Confidence must be between 0 and 1")
        
        # Validate sources if present
        if "sources" in response_data:
            sources = response_data["sources"]
            if not isinstance(sources, list):
                raise ValidationError("Sources must be a list")
            for source in sources:
                if not isinstance(source, dict):
                    raise ValidationError("Each source must be a dictionary")
                if "title" not in source:
                    raise ValidationError("Each source must have a 'title' field")
                if "type" in source and source["type"] not in ["web", "book", "paper", "documentation"]:
                    raise ValidationError(f"Invalid source type: {source['type']}")
        
        # Validate follow_up_questions if present
        if "follow_up_questions" in response_data:
            questions = response_data["follow_up_questions"]
            if not isinstance(questions, list):
                raise ValidationError("Follow-up questions must be a list")
            for question in questions:
                if not isinstance(question, str) or not question.strip():
                    raise ValidationError("Each follow-up question must be a non-empty string")
        
        # Validate difficulty_level if present
        if "difficulty_level" in response_data:
            level = response_data["difficulty_level"]
            if level not in ["beginner", "intermediate", "advanced"]:
                raise ValidationError("Difficulty level must be 'beginner', 'intermediate', or 'advanced'")
        
        # Validate tags if present
        if "tags" in response_data:
            tags = response_data["tags"]
            if not isinstance(tags, list):
                raise ValidationError("Tags must be a list")
            for tag in tags:
                if not isinstance(tag, str) or not tag.strip():
                    raise ValidationError("Each tag must be a non-empty string")
        
        # Validate examples if present
        if "examples" in response_data:
            examples = response_data["examples"]
            if not isinstance(examples, list):
                raise ValidationError("Examples must be a list")
            for example in examples:
                if not isinstance(example, dict):
                    raise ValidationError("Each example must be a dictionary")
                if "description" not in example:
                    raise ValidationError("Each example must have a 'description' field")
        
        return True
