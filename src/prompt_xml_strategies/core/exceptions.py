"""Custom exceptions for the framework."""


class PromptXMLError(Exception):
    """Base exception for all framework errors."""
    pass


class ValidationError(PromptXMLError):
    """Exception raised when validation fails."""
    pass


class TemplateError(PromptXMLError):
    """Exception raised when template rendering fails."""
    pass


class PipelineError(PromptXMLError):
    """Exception raised when pipeline execution fails."""
    pass


class StrategyError(PromptXMLError):
    """Exception raised by strategy operations."""
    pass


class SchemaError(PromptXMLError):
    """Exception raised when schema operations fail."""
    pass


class TransformationError(PromptXMLError):
    """Exception raised when data transformation fails."""
    pass