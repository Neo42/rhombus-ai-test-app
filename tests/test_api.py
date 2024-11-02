import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

pytestmark = [pytest.mark.asyncio, pytest.mark.django_db]


class TestFileUploadAPI:
    """Tests for the file upload API."""

    async def test_file_upload_success(self, async_client, csv_file):
        """Test successful file upload flow"""
        response = await async_client.post("/api/upload", {"file": csv_file})
        assert response.status_code == 201
        data = response.json()
        assert "file_id" in data
        assert "message" in data

    async def test_invalid_file_upload(self, async_client):
        """Test upload with invalid file type"""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"invalid content",
            content_type="text/plain",  # Invalid content type
        )

        try:
            response = await async_client.post("/api/upload", {"file": invalid_file})
            assert response.status_code == 422
        except ValueError:
            # If the service raises ValueError directly
            pytest.raises(
                ValueError, response.raise_for_status(), match="Upload failed"
            )

    async def test_empty_file_upload(self, async_client):
        """Test upload with empty file"""
        empty_file = SimpleUploadedFile("empty.csv", b"", content_type="text/csv")
        print(empty_file.size)

        response = await async_client.post("/api/upload", {"file": empty_file})
        assert response.status_code == 422
