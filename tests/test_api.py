import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import AsyncClient

pytestmark = [pytest.mark.asyncio, pytest.mark.django_db]


class TestFileUploadAPI:
    """Tests for the file upload API."""

    @pytest.mark.asyncio
    async def test_file_upload_success(self, async_client: AsyncClient):
        """Test successful file upload flow"""
        csv_content = b"col1,col2\n1,2\n3,4"
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")

        response = await async_client.post("/api/upload", {"file": csv_file})

        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert data["message"] == "File uploaded successfully"

    @pytest.mark.asyncio
    async def test_invalid_file_upload(self, async_client: AsyncClient):
        """Test upload with invalid file type"""
        invalid_file = SimpleUploadedFile(
            "test.txt", b"invalid content", content_type="text/plain"
        )

        response = await async_client.post("/api/upload", {"file": invalid_file})

        assert response.status_code == 400
        data = response.json()
        assert "Invalid file type" in data["detail"]

    @pytest.mark.asyncio
    async def test_empty_file_upload(self, async_client: AsyncClient):
        """Test upload with empty file"""
        empty_file = SimpleUploadedFile("empty.csv", b"", content_type="text/csv")

        response = await async_client.post("/api/upload", {"file": empty_file})

        assert response.status_code == 400
        data = response.json()
        assert "File is empty" in data["detail"]
