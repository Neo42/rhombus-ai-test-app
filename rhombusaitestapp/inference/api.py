"""API for the Inference app."""

import logging

from django.http import HttpRequest
from ninja import NinjaAPI, UploadedFile
from ninja.errors import HttpError
from ninja.responses import Response

from .constants import ErrorCodes
from .exceptions import (
    ColumnNotFoundError,
    FileNotProcessedError,
    FileValidationError,
    InvalidColumnTypeError,
)
from .models import DataFile
from .schemas import (
    DataFileResponseSchema,
    DataTypeOverrideResponseSchema,
    DataTypeOverrideSchema,
    ErrorResponseSchema,
    FileUploadResponseSchema,
)
from .services import FileProcessingService

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize API
api = NinjaAPI(urls_namespace="inference_api", version="1.0.0")
service = FileProcessingService()


@api.post(
    "/upload",
    response={
        201: FileUploadResponseSchema,
        400: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
async def upload_file(
    request: HttpRequest,
    file: UploadedFile,
) -> Response:
    """Upload and queue file for processing."""
    try:
        result = await service.handle_upload(file)
        return Response({"file_id": result.id, "message": "File uploaded successfully"}, status=201)
    except FileValidationError as exc:
        logger.warning("File validation failed: %s", str(exc), extra={"file": file.name})
        raise HttpError(400, f"{ErrorCodes.VALIDATION_ERROR}: {exc!s}") from exc
    except HttpError:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during file upload")
        raise HttpError(500, f"{ErrorCodes.INTERNAL_ERROR}: Internal server error") from exc


@api.get(
    "/files/{file_id}",
    response={
        200: DataFileResponseSchema,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
def get_file_status(request: HttpRequest, file_id: int) -> dict:
    """Get current processing status."""
    try:
        data_file = service.get_file(file_id)
        return {
            "id": data_file.id,
            "original_filename": data_file.original_filename,
            "uploaded_at": data_file.uploaded_at,
            "processing_status": data_file.processing_status,
            "processing_time": data_file.processing_time,
            "error_message": data_file.error_message,
            "inferred_types": data_file.inferred_types,
            "overridden_types": data_file.overridden_types,
            "effective_types": data_file.get_column_types(),
            "row_count": data_file.row_count,
            "column_count": data_file.column_count,
            "sample_data": data_file.sample_data,
        }
    except DataFile.DoesNotExist as exc:
        logger.warning("File not found: %s", file_id)
        raise HttpError(404, f"{ErrorCodes.FILE_NOT_FOUND}: File not found") from exc
    except Exception as exc:
        logger.exception("Unexpected error retrieving file status")
        raise HttpError(500, f"{ErrorCodes.INTERNAL_ERROR}: Internal server error") from exc


@api.patch(
    "/files/{file_id}/columns/{column_name}",
    response={
        200: DataTypeOverrideResponseSchema,
        400: ErrorResponseSchema,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
def update_column_type(
    request: HttpRequest,
    file_id: int,
    column_name: str,
    payload: DataTypeOverrideSchema,
) -> dict:
    """Update the data type for a specific column."""
    try:
        return service.override_column_type(
            file_id=file_id,
            column_name=column_name,
            custom_type=payload.custom_type,
        )
    except FileNotProcessedError as exc:
        logger.warning("File not processed: %s", file_id)
        raise HttpError(400, f"{ErrorCodes.PROCESSING_INCOMPLETE}: {exc!s}") from exc
    except ColumnNotFoundError as exc:
        logger.warning("Column not found: %s in file %s", column_name, file_id)
        raise HttpError(404, f"{ErrorCodes.COLUMN_NOT_FOUND}: {exc!s}") from exc
    except InvalidColumnTypeError as exc:
        logger.warning(
            "Invalid column type: %s for %s in file %s",
            payload.custom_type,
            column_name,
            file_id,
        )
        raise HttpError(400, f"{ErrorCodes.INVALID_COLUMN_TYPE}: {exc!s}") from exc
    except DataFile.DoesNotExist as exc:
        logger.warning("File not found: %s", file_id)
        raise HttpError(404, f"{ErrorCodes.FILE_NOT_FOUND}: File not found") from exc
    except Exception as exc:
        logger.exception("Unexpected error updating column type")
        raise HttpError(500, f"{ErrorCodes.INTERNAL_ERROR}: Internal server error") from exc
