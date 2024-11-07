"""Services for the Rhombus AI Test App."""

from typing import ClassVar

from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from .constants import DataTypeConfig, ErrorMessages, ProcessingStatus
from .exceptions import (
    ColumnNotFoundError,
    FileNotProcessedError,
    InvalidColumnTypeError,
)
from .models import DataFile
from .tasks import process_file


class FileProcessingService:
    """Service for processing file uploads."""

    # Define allowed file types and size limits
    ALLOWED_CONTENT_TYPES: ClassVar[set[str]] = {
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
        "application/vnd.ms-excel",  # xls
    }
    MAX_FILE_SIZE: ClassVar[int] = 1024 * 1024 * 1024  # 1GB

    def validate_file(self: "FileProcessingService", file: UploadedFile) -> None:
        """Validate uploaded file."""
        if not file:
            raise HttpError(400, "No file was submitted")

        # Check file size
        if file.size is not None and file.size > self.MAX_FILE_SIZE:
            msg = f"File size cannot exceed {self.MAX_FILE_SIZE // (1024*1024)}MB"
            raise HttpError(400, msg)

        # Check if file is empty
        if file.size == 0:
            raise HttpError(400, "File is empty")

        # Validate content type
        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            msg = f"Invalid file type. Allowed types are: {', '.join(self.ALLOWED_CONTENT_TYPES)}"
            raise HttpError(400, msg)

    async def handle_upload(self: "FileProcessingService", file: UploadedFile) -> DataFile:
        """Handle file upload and queue processing."""
        # Validate file
        self.validate_file(file)

        # Save file
        data_file = await DataFile.objects.acreate(
            file=file,
            original_filename=file.name,
            processing_status=ProcessingStatus.UPLOADING.value,
        )

        # Queue processing task
        process_file.delay(data_file.id)

        return data_file

    def get_file(self: "FileProcessingService", file_id: int) -> DataFile:
        """Get current processing status."""
        return get_object_or_404(DataFile, id=file_id)

    def get_preview(self: "FileProcessingService", file_id: int) -> dict:
        """Get file preview data."""
        data_file = get_object_or_404(DataFile, id=file_id)

        if data_file.processing_status != ProcessingStatus.INFERRED:
            return {
                "processing_status": data_file.processing_status,
                "error": ErrorMessages.FILE_NOT_READY_FOR_PREVIEW,
            }

        return {
            "processing_status": data_file.processing_status,
            "sample_data": data_file.sample_data,
            "column_types": data_file.get_column_types(),
            "row_count": data_file.row_count,
            "column_count": data_file.column_count,
        }

    def override_column_type(
        self: "FileProcessingService",
        file_id: int,
        column_name: str,
        custom_type: str,
    ) -> dict:
        """Override the data type for a specific column."""
        data_file = self.get_file(file_id)

        # Business logic validations
        if data_file.processing_status != ProcessingStatus.INFERRED:
            raise FileNotProcessedError("File must be processed before overriding column types")

        if not data_file.inferred_types or column_name not in data_file.inferred_types:
            raise ColumnNotFoundError(f"Column '{column_name}' not found")

        if not DataTypeConfig.is_valid_type(custom_type):
            raise InvalidColumnTypeError("Invalid type. Must be a string starting with a letter.")

        # Update type if validations pass
        data_file.override_column_type(column_name, custom_type)

        return {
            "column_name": column_name,
            "original_type": data_file.inferred_types[column_name],
            "custom_type": custom_type,
            "effective_types": data_file.get_column_types(),
        }
