"""Custom exceptions for the inference app."""


class InferenceError(Exception):
    """Base exception for inference app."""


class FileNotProcessedError(InferenceError):
    """Raised when attempting operations on unprocessed files."""


class ColumnNotFoundError(InferenceError):
    """Raised when column is not found in file."""


class InvalidColumnTypeError(InferenceError):
    """Raised when invalid column type is specified."""


class FileValidationError(InferenceError):
    """Raised when file validation fails."""
