"""XML output strategies package."""

from .interface import XmlOutputStrategy
from .simple_xml_strategy import SimpleXmlOutputStrategy
from .qa_xml_output_strategy import QAXmlOutputStrategy

__all__ = ['XmlOutputStrategy', 'SimpleXmlOutputStrategy', 'QAXmlOutputStrategy']