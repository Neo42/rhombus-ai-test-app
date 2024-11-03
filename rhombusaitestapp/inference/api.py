"""API for the Inference app."""

from django.http import HttpRequest
from ninja import NinjaAPI, UploadedFile
from ninja.errors import HttpError
from ninja.responses import Response

from .models import DataFile
from .schemas import DataFileResponseSchema, FileUploadResponseSchema
from .services import FileProcessingService

# Initialize API
api = NinjaAPI(urls_namespace="inference_api", version="1.0.0")
service = FileProcessingService()


@api.post("/upload", response={201: FileUploadResponseSchema})
async def upload_file(
    request: HttpRequest,
    file: UploadedFile,
) -> Response:
    """Upload and queue file for processing."""
    try:
        result = await service.handle_upload(file)
        return Response(
            {"file_id": result.id, "message": "File uploaded successfully"}, status=201
        )
    except HttpError as e:
        raise e from e
    except Exception as e:
        raise HttpError(500, str(e)) from e


@api.get("/files/{file_id}", response=DataFileResponseSchema)
def get_file_status(request: HttpRequest, file_id: int) -> DataFile:
    """Get current processing status."""
    return service.get_status(file_id)
