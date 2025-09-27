"""XML output strategies package."""

from .interface import XmlOutputStrategy
from .simple_xml_strategy import SimpleXmlOutputStrategy

__all__ = ['XmlOutputStrategy', 'SimpleXmlOutputStrategy']