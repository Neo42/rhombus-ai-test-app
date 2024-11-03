"""Constants used throughout the inference app."""

from enum import Enum
from typing import ClassVar, Self


class ProcessingStatus(str, Enum):
    """Enum for file processing status values."""

    IDLE = "IDLE"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    INFERRING = "INFERRING"
    INFERRED = "INFERRED"
    INFERENCE_FAILED = "INFERENCE_FAILED"

    @classmethod
    def choices(cls: type[Self]) -> list[tuple[str, str]]:
        """Return choices for Django model field."""
        return [(status, status.display_name) for status in cls]

    @property
    def display_name(self: Self) -> str:
        """Return human-readable status name."""
        return {
            self.IDLE: "Idle",
            self.UPLOADING: "Uploading",
            self.UPLOADED: "Upload Complete",
            self.UPLOAD_FAILED: "Upload Failed",
            self.INFERRING: "Inferring Types",
            self.INFERRED: "Inference Complete",
            self.INFERENCE_FAILED: "Inference Failed",
        }[self]

    @classmethod
    def from_str(cls: type[Self], value: str) -> Self:
        """Convert string to enum value."""
        try:
            return cls(value)
        except ValueError as e:
            raise ValueError(f"'{value}' is not a valid {cls.__name__}") from e

    def __str__(self: Self) -> str:
        """Return string representation."""
        return self.value


class HttpStatus(int, Enum):
    """HTTP status codes used in the API."""

    OK = 200
    CREATED = 201
    BAD_REQUEST = 400


class CacheConfig:
    """Cache-related configuration."""

    TIMEOUT = 60  # seconds
    KEY_PREFIX = "process_file_"

    @classmethod
    def get_key(cls: type[Self], file_id: int) -> str:
        """Generate cache key for a file."""
        return f"{cls.KEY_PREFIX}{file_id}"


class DataTypeConfig:
    """Configuration for data type inference."""

    TYPES: ClassVar[list[dict[str, str]]] = [
        {
            "internal_name": "object",
            "display_name": "Text",
            "description": "Text data",
        },
        {
            "internal_name": "int64",
            "display_name": "Integer",
            "description": "Whole numbers",
        },
        {
            "internal_name": "float64",
            "display_name": "Float",
            "description": "Floating point numbers",
        },
        {
            "internal_name": "bool",
            "display_name": "Boolean",
            "description": "True/False values",
        },
        {
            "internal_name": "category",
            "display_name": "Category",
            "description": "Categorical data",
        },
        {
            "internal_name": "complex",
            "display_name": "Complex Number",
            "description": "Complex numbers",
        },
        {
            "internal_name": "datetime",
            "display_name": "Date/Time",
            "description": "Date and time data",
        },
        {
            "internal_name": "timedelta",
            "display_name": "Time Interval",
            "description": "Time intervals",
        },
    ]

    @classmethod
    def is_valid_type(cls: type[Self], type_name: str) -> bool:
        """Check if type name is valid by checking if it starts with a string.

        Args:
            type_name: The type name to validate

        Returns:
            bool: True if type name starts with a string

        """
        return isinstance(type_name, str) and bool(type_name.strip())


class ErrorMessages:
    """Error messages used throughout the application."""

    FILE_NOT_READY_FOR_PREVIEW = "File is not ready for preview"
    FILE_NOT_READY_FOR_INFERENCE = "File is not ready for inference"
    INFERENCE_FAILED = "Inference failed"


class ErrorCodes:
    """Error codes for API responses."""

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_EMPTY = "FILE_EMPTY"

    # Not found errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    COLUMN_NOT_FOUND = "COLUMN_NOT_FOUND"

    # Processing errors
    PROCESSING_INCOMPLETE = "PROCESSING_INCOMPLETE"
    PROCESSING_FAILED = "PROCESSING_FAILED"

    # Type errors
    INVALID_COLUMN_TYPE = "INVALID_COLUMN_TYPE"

    # Generic errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
