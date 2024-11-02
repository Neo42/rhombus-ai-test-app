"""Schemas for the Rhombus AI Test App."""

from datetime import datetime
from typing import Any

from ninja import Schema


class DataTypeSchema(Schema):
    """Schema for mapping internal data types to user-friendly names."""

    internal_name: str  # e.g., "object", "int64"
    display_name: str  # e.g., "Text", "Number"
    description: str | None = None


class ColumnInfoSchema(Schema):
    """Schema for column information."""

    name: str
    inferred_type: str
    sample_values: list[Any]


class DataFileResponseSchema(Schema):
    """Schema for file processing response."""

    id: int
    original_filename: str
    uploaded_at: datetime
    processing_status: str
    processing_time: float | None
    error_message: str | None
    inferred_types: dict[str, str] | None
    row_count: int | None
    column_count: int | None
    sample_data: list[dict[str, Any]] | None


class DataTypeOverrideSchema(Schema):
    """Schema for overriding column data types."""

    column_name: str
    new_type: str


class FileUploadResponseSchema(Schema):
    """Schema for file upload response."""

    file_id: int
    message: str = "File uploaded successfully"
