"""Constants used throughout the inference app."""

from enum import Enum
from typing import ClassVar


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
    def choices(cls: "ProcessingStatus") -> list[tuple[str, str]]:
        """Return choices for Django model field."""
        return [(status.value, status.display_name) for status in cls]

    @property
    def display_name(self: "ProcessingStatus") -> str:
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
    def get_key(cls: "CacheConfig", file_id: int) -> str:
        """Generate cache key for a file."""
        return f"{cls.KEY_PREFIX}{file_id}"


class DataTypeConfig:
    """Configuration for data type inference."""

    MAX_SAMPLE_VALUES = 5

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
    def get_valid_types(cls: "DataTypeConfig") -> list[str]:
        """Return list of valid internal type names."""
        return [dt["internal_name"] for dt in cls.TYPES]


class ErrorMessages:
    """Error messages used throughout the application."""

    FILE_NOT_READY_FOR_PREVIEW = "File is not ready for preview"
    FILE_NOT_READY_FOR_INFERENCE = "File is not ready for inference"
    INFERENCE_FAILED = "Inference failed"
