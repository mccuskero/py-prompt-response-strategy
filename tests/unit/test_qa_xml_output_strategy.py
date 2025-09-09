"""Tests for the QAXmlOutputStrategy class."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from xml.etree.ElementTree import Element, tostring

from prompt_xml_strategies.xml_output_strategies.qa_xml_output_strategy import QAXmlOutputStrategy


class TestQAXmlOutputStrategy:
    """Test cases for QAXmlOutputStrategy class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary XSD file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.xsd_file = os.path.join(self.temp_dir, "test_qa_schema.xsd")
        
        # Sample XSD data
        self.xsd_data = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="https://test.dev/schemas/xsd/conversational"
           xmlns:tns="https://test.dev/schemas/xsd/conversational"
           elementFormDefault="qualified">

  <xs:element name="qa_response" type="tns:QAResponseType"/>

  <xs:complexType name="QAResponseType">
    <xs:sequence>
      <xs:element name="answer" type="xs:string"/>
      <xs:element name="confidence" type="tns:ConfidenceType" minOccurs="0"/>
      <xs:element name="sources" type="tns:SourcesType" minOccurs="0"/>
      <xs:element name="follow_up_questions" type="tns:FollowUpQuestionsType" minOccurs="0"/>
      <xs:element name="explanation" type="xs:string" minOccurs="0"/>
      <xs:element name="examples" type="tns:ExamplesType" minOccurs="0"/>
      <xs:element name="difficulty_level" type="tns:DifficultyLevelType" minOccurs="0"/>
      <xs:element name="tags" type="tns:TagsType" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>

  <xs:simpleType name="ConfidenceType">
    <xs:restriction base="xs:decimal">
      <xs:minInclusive value="0"/>
      <xs:maxInclusive value="1"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:complexType name="SourcesType">
    <xs:sequence>
      <xs:element name="source" type="tns:SourceType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <xs:complexType name="SourceType">
    <xs:sequence>
      <xs:element name="title" type="xs:string"/>
      <xs:element name="url" type="xs:anyURI" minOccurs="0"/>
      <xs:element name="type" type="tns:SourceTypeEnum" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>

  <xs:simpleType name="SourceTypeEnum">
    <xs:restriction base="xs:string">
      <xs:enumeration value="web"/>
      <xs:enumeration value="book"/>
      <xs:enumeration value="paper"/>
      <xs:enumeration value="documentation"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:complexType name="FollowUpQuestionsType">
    <xs:sequence>
      <xs:element name="question" type="xs:string" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <xs:complexType name="ExamplesType">
    <xs:sequence>
      <xs:element name="example" type="tns:ExampleType" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

  <xs:complexType name="ExampleType">
    <xs:sequence>
      <xs:element name="description" type="xs:string"/>
      <xs:element name="code" type="xs:string" minOccurs="0"/>
      <xs:element name="output" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>

  <xs:simpleType name="DifficultyLevelType">
    <xs:restriction base="xs:string">
      <xs:enumeration value="beginner"/>
      <xs:enumeration value="intermediate"/>
      <xs:enumeration value="advanced"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:complexType name="TagsType">
    <xs:sequence>
      <xs:element name="tag" type="xs:string" maxOccurs="unbounded"/>
    </xs:sequence>
  </xs:complexType>

</xs:schema>'''
        
        # Write XSD to temporary file
        with open(self.xsd_file, 'w') as f:
            f.write(self.xsd_data)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_with_custom_xsd_path(self):
        """Test initialization with custom XSD path."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        assert strategy.xsd_path == self.xsd_file
        assert strategy.xsd_schema is not None
        assert strategy.namespace == "https://prompt-xml-strategies.dev/schemas/xsd/conversational"
    
    def test_initialization_with_default_xsd_path(self):
        """Test initialization with default XSD path."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('xmlschema.XMLSchema') as mock_xmlschema:
                mock_xmlschema.return_value = Mock()
                strategy = QAXmlOutputStrategy()
                
                assert strategy.xsd_path is not None
                assert strategy.xsd_schema is not None
    
    def test_initialization_xsd_file_not_found(self):
        """Test initialization when XSD file is not found."""
        with pytest.raises(FileNotFoundError):
            QAXmlOutputStrategy(xsd_path="nonexistent.xsd")
    
    def test_initialization_invalid_xsd(self):
        """Test initialization with invalid XSD schema."""
        invalid_xsd_file = os.path.join(self.temp_dir, "invalid.xsd")
        with open(invalid_xsd_file, 'w') as f:
            f.write("invalid xsd content")
        
        with pytest.raises(ValueError, match="Invalid XSD schema file"):
            QAXmlOutputStrategy(xsd_path=invalid_xsd_file)
    
    def test_transform_to_xml_minimal_response(self):
        """Test XML transformation with minimal required data."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "This is a test answer"
        }
        
        xml_element = strategy.transform_to_xml(response_data)
        
        assert xml_element.tag == f"{{{strategy.namespace}}}qa_response"
        
        # Check answer element
        answer_elem = xml_element.find(f"{{{strategy.namespace}}}answer")
        assert answer_elem is not None
        assert answer_elem.text == "This is a test answer"
    
    def test_transform_to_xml_complete_response(self):
        """Test XML transformation with complete response data."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "This is a comprehensive answer",
            "confidence": 0.95,
            "sources": [
                {
                    "title": "Test Source",
                    "url": "https://example.com",
                    "type": "web"
                }
            ],
            "follow_up_questions": ["What else?", "How about this?"],
            "explanation": "This is a detailed explanation",
            "examples": [
                {
                    "description": "Example 1",
                    "code": "print('hello')",
                    "output": "hello"
                }
            ],
            "difficulty_level": "intermediate",
            "tags": ["test", "example"]
        }
        
        xml_element = strategy.transform_to_xml(response_data)
        
        assert xml_element.tag == f"{{{strategy.namespace}}}qa_response"
        
        # Check all elements are present
        assert xml_element.find(f"{{{strategy.namespace}}}answer").text == "This is a comprehensive answer"
        assert xml_element.find(f"{{{strategy.namespace}}}confidence").text == "0.95"
        assert xml_element.find(f"{{{strategy.namespace}}}explanation").text == "This is a detailed explanation"
        assert xml_element.find(f"{{{strategy.namespace}}}difficulty_level").text == "intermediate"
        
        # Check sources
        sources_elem = xml_element.find(f"{{{strategy.namespace}}}sources")
        assert sources_elem is not None
        source_elem = sources_elem.find(f"{{{strategy.namespace}}}source")
        assert source_elem.find(f"{{{strategy.namespace}}}title").text == "Test Source"
        assert source_elem.find(f"{{{strategy.namespace}}}url").text == "https://example.com"
        assert source_elem.find(f"{{{strategy.namespace}}}type").text == "web"
        
        # Check follow-up questions
        questions_elem = xml_element.find(f"{{{strategy.namespace}}}follow_up_questions")
        assert questions_elem is not None
        question_elems = questions_elem.findall(f"{{{strategy.namespace}}}question")
        assert len(question_elems) == 2
        assert question_elems[0].text == "What else?"
        assert question_elems[1].text == "How about this?"
        
        # Check examples
        examples_elem = xml_element.find(f"{{{strategy.namespace}}}examples")
        assert examples_elem is not None
        example_elem = examples_elem.find(f"{{{strategy.namespace}}}example")
        assert example_elem.find(f"{{{strategy.namespace}}}description").text == "Example 1"
        assert example_elem.find(f"{{{strategy.namespace}}}code").text == "print('hello')"
        assert example_elem.find(f"{{{strategy.namespace}}}output").text == "hello"
        
        # Check tags
        tags_elem = xml_element.find(f"{{{strategy.namespace}}}tags")
        assert tags_elem is not None
        tag_elems = tags_elem.findall(f"{{{strategy.namespace}}}tag")
        assert len(tag_elems) == 2
        assert tag_elems[0].text == "test"
        assert tag_elems[1].text == "example"
    
    def test_transform_to_xml_with_context(self):
        """Test XML transformation with context information."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {"answer": "Test answer"}
        context = {"user_id": "test_user", "session_id": "session_123"}
        
        xml_element = strategy.transform_to_xml(response_data, context)
        
        assert xml_element.get("context_user_id") == "test_user"
        assert xml_element.get("context_session_id") == "session_123"
    
    def test_transform_to_xml_missing_required_field(self):
        """Test XML transformation with missing required field."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {"confidence": 0.8}  # Missing required "answer" field
        
        with pytest.raises(Exception, match="Q&A response must contain an 'answer' field"):
            strategy.transform_to_xml(response_data)
    
    def test_transform_to_xml_invalid_confidence(self):
        """Test XML transformation with invalid confidence value."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "Test answer",
            "confidence": 1.5  # Invalid confidence > 1
        }
        
        with pytest.raises(Exception, match="Confidence must be between 0 and 1"):
            strategy.transform_to_xml(response_data)
    
    def test_transform_to_xml_invalid_source_type(self):
        """Test XML transformation with invalid source type."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "Test answer",
            "sources": [{"title": "Test", "type": "invalid_type"}]
        }
        
        with pytest.raises(Exception, match="Invalid source type: invalid_type"):
            strategy.transform_to_xml(response_data)
    
    def test_transform_to_xml_invalid_difficulty_level(self):
        """Test XML transformation with invalid difficulty level."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "Test answer",
            "difficulty_level": "expert"  # Invalid level
        }
        
        with pytest.raises(Exception, match="Invalid difficulty level: expert"):
            strategy.transform_to_xml(response_data)
    
    def test_transform_to_xml_invalid_input_type(self):
        """Test XML transformation with invalid input type."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        with pytest.raises(Exception, match="Response data must be a dictionary"):
            strategy.transform_to_xml("not a dict")
    
    def test_validate_xml_valid(self):
        """Test XML validation with valid XML."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        # Create a valid XML element
        response_data = {
            "answer": "This is a valid answer",
            "confidence": 0.8,
            "difficulty_level": "intermediate"
        }
        
        xml_element = strategy.transform_to_xml(response_data)
        
        # Mock the XSD validation to return True
        with patch.object(strategy.xsd_schema, 'validate', return_value=True):
            assert strategy.validate_xml(xml_element) is True
    
    def test_validate_xml_invalid(self):
        """Test XML validation with invalid XML."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        # Create an invalid XML element (missing required answer)
        xml_element = Element(f"{{{strategy.namespace}}}qa_response")
        
        # Mock the XSD validation to raise an exception
        with patch.object(strategy.xsd_schema, 'validate', side_effect=Exception("Validation failed")):
            with pytest.raises(Exception, match="XML validation failed"):
                strategy.validate_xml(xml_element)
    
    def test_validate_xml_no_schema(self):
        """Test XML validation when schema is not loaded."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        strategy.xsd_schema = None
        
        xml_element = Element("test")
        
        with pytest.raises(Exception, match="XSD schema not loaded"):
            strategy.validate_xml(xml_element)
    
    def test_get_strategy_info(self):
        """Test getting strategy information."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        info = strategy.get_strategy_info()
        
        assert info["name"] == "QAXmlOutputStrategy"
        assert info["version"] == "1.0.0"
        assert info["description"] == "Generates Q&A XML output using XSD schema validation"
        assert info["xsd_path"] == self.xsd_file
        assert info["xsd_loaded"] is True
        assert info["namespace"] == "https://prompt-xml-strategies.dev/schemas/xsd/conversational"
        assert info["supports_validation"] is True
        assert info["supports_namespaces"] is True
    
    def test_get_xsd_info(self):
        """Test getting XSD schema information."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        xsd_info = strategy.get_xsd_info()
        
        assert xsd_info["loaded"] is True
        assert "target_namespace" in xsd_info
        assert "elements" in xsd_info
        assert "types" in xsd_info
    
    def test_get_xsd_info_no_schema(self):
        """Test getting XSD info when schema is not loaded."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        strategy.xsd_schema = None
        
        xsd_info = strategy.get_xsd_info()
        
        assert xsd_info["loaded"] is False
    
    def test_reload_xsd(self):
        """Test reloading XSD schema from file."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        # Create a new XSD file
        new_xsd_file = os.path.join(self.temp_dir, "new_qa_schema.xsd")
        with open(new_xsd_file, 'w') as f:
            f.write(self.xsd_data)
        
        # Reload with new XSD
        strategy.reload_xsd(new_xsd_file)
        
        assert strategy.xsd_path == new_xsd_file
        assert strategy.xsd_schema is not None
    
    def test_get_schema_elements(self):
        """Test getting schema elements."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        elements = strategy.get_schema_elements()
        
        # Should contain at least the main qa_response element
        assert "qa_response" in elements
    
    def test_get_schema_types(self):
        """Test getting schema types."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        types = strategy.get_schema_types()
        
        # Should contain various types defined in the schema
        assert len(types) > 0
    
    def test_validate_response_data_valid(self):
        """Test response data validation with valid data."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "This is a valid answer",
            "confidence": 0.8,
            "sources": [{"title": "Test Source", "type": "web"}],
            "follow_up_questions": ["What else?"],
            "difficulty_level": "intermediate",
            "tags": ["test"],
            "examples": [{"description": "Example"}]
        }
        
        assert strategy.validate_response_data(response_data) is True
    
    def test_validate_response_data_missing_answer(self):
        """Test response data validation with missing answer."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {"confidence": 0.8}
        
        with pytest.raises(Exception, match="Q&A response must contain an 'answer' field"):
            strategy.validate_response_data(response_data)
    
    def test_validate_response_data_invalid_confidence(self):
        """Test response data validation with invalid confidence."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "Test answer",
            "confidence": 1.5
        }
        
        with pytest.raises(Exception, match="Confidence must be between 0 and 1"):
            strategy.validate_response_data(response_data)
    
    def test_validate_response_data_invalid_source_type(self):
        """Test response data validation with invalid source type."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "Test answer",
            "sources": [{"title": "Test", "type": "invalid"}]
        }
        
        with pytest.raises(Exception, match="Invalid source type: invalid"):
            strategy.validate_response_data(response_data)
    
    def test_validate_response_data_invalid_difficulty_level(self):
        """Test response data validation with invalid difficulty level."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {
            "answer": "Test answer",
            "difficulty_level": "expert"
        }
        
        with pytest.raises(Exception, match="Difficulty level must be 'beginner', 'intermediate', or 'advanced'"):
            strategy.validate_response_data(response_data)
    
    def test_validate_response_data_invalid_input_type(self):
        """Test response data validation with invalid input type."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        with pytest.raises(Exception, match="Response data must be a dictionary"):
            strategy.validate_response_data("not a dict")
    
    def test_xml_namespace_handling(self):
        """Test that XML elements are created with proper namespaces."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {"answer": "Test answer"}
        xml_element = strategy.transform_to_xml(response_data)
        
        # Check that the root element has the correct namespace
        assert xml_element.tag == f"{{{strategy.namespace}}}qa_response"
        
        # Check that child elements also have the namespace
        answer_elem = xml_element.find(f"{{{strategy.namespace}}}answer")
        assert answer_elem is not None
        assert answer_elem.tag == f"{{{strategy.namespace}}}answer"
    
    def test_xml_timestamp_generation(self):
        """Test that XML elements include timestamps."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {"answer": "Test answer"}
        xml_element = strategy.transform_to_xml(response_data)
        
        # Verify the XML element was created successfully
        assert xml_element.tag == f"{{{strategy.namespace}}}qa_response"
    
    def test_xml_context_attributes(self):
        """Test that context information is added as XML attributes."""
        strategy = QAXmlOutputStrategy(xsd_path=self.xsd_file)
        
        response_data = {"answer": "Test answer"}
        context = {
            "user_id": "user123",
            "session_id": "session456",
            "complex_data": {"nested": "value"}  # Should be ignored
        }
        
        xml_element = strategy.transform_to_xml(response_data, context)
        
        assert xml_element.get("context_user_id") == "user123"
        assert xml_element.get("context_session_id") == "session456"
        assert xml_element.get("context_complex_data") is None  # Complex data should be ignored
