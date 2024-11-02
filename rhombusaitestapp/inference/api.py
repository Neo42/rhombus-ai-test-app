"""API for the Inference app."""

from urllib.request import Request

from ninja import NinjaAPI, UploadedFile
from ninja.responses import Response

from .schemas import DataFileResponseSchema, FileUploadResponseSchema
from .services import FileProcessingService

# Create API with custom error handler
api = NinjaAPI()
service = FileProcessingService()


@api.exception_handler(ValueError)
def validation_error_handler(request: Request, exc: ValueError) -> Response:
    """Convert ValueError to HTTP 422 response."""
    return api.create_response(
        request,
        {"detail": str(exc)},
        status=422,
    )


@api.post("/upload", response={201: FileUploadResponseSchema})
async def upload_file(
    request: Request, file: UploadedFile = None
) -> FileUploadResponseSchema:
    """Upload and queue file for processing."""
    result = await service.handle_upload(file)
    return 201, result


@api.get("/files/{file_id}", response=DataFileResponseSchema)
def get_file_status(request: Request, file_id: int) -> DataFileResponseSchema:
    """Get current processing status."""
    return service.get_status(file_id)
