"""Models for the Rhombus AI Test App."""

from typing import Any

from django.core.validators import FileExtensionValidator
from django.db import models

from .constants import DataTypeConfig, ProcessingStatus


class DataType(models.Model):
    """Model for mapping internal data types to user-friendly names."""

    internal_name = models.CharField(max_length=50)  # e.g., "object", "int64"
    display_name = models.CharField(max_length=50)  # e.g., "Text", "Number"
    description = models.TextField(blank=True)

    def __str__(self: "DataType") -> str:
        """Return a string representation of the DataType."""
        return f"{self.display_name} ({self.internal_name})"


class DataFile(models.Model):
    """Model for storing uploaded data files and their processing results."""

    file = models.FileField(
        upload_to="uploads/",
        validators=[FileExtensionValidator(allowed_extensions=["csv", "xlsx", "xls"])],
    )
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices(),
        default=ProcessingStatus.IDLE,
    )
    processing_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(default="", blank=True)

    # Store column metadata
    inferred_types = models.JSONField(null=True, blank=True)
    overridden_types = models.JSONField(null=True, blank=True)
    sample_data = models.JSONField(null=True, blank=True)

    row_count = models.IntegerField(null=True, blank=True)
    column_count = models.IntegerField(null=True, blank=True)

    def __str__(self: "DataFile") -> str:
        """Return a string representation of the DataFile."""
        return f"{self.original_filename} ({self.processing_status})"

    def get_column_types(self: "DataFile") -> dict[str, Any]:
        """Get the effective column types, considering overrides."""
        if not self.inferred_types:
            return {}

        effective_types = self.inferred_types.copy()
        if self.overridden_types:
            effective_types.update(self.overridden_types)
        return effective_types

    def validate_column_type(
        self: "DataFile",
        column_name: str,
        custom_type: str,
    ) -> None:
        """Validate column type override."""
        if not self.inferred_types or column_name not in self.inferred_types:
            raise ValueError(f"Column '{column_name}' not found")

        if not DataTypeConfig.is_valid_type(custom_type):
            raise ValueError(f"Invalid type '{custom_type}'. Must be a string starting with a letter.")

    def override_column_type(
        self: "DataFile",
        column_name: str,
        custom_type: str,
    ) -> None:
        """Override the data type for a column."""
        self.validate_column_type(column_name, custom_type)

        overridden_types = self.overridden_types or {}
        overridden_types[column_name] = custom_type
        self.overridden_types = overridden_types
        self.save()
