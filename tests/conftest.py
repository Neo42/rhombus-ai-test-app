"""Fixtures for the tests."""

import contextlib

import pytest
from asgiref.sync import sync_to_async
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import AsyncClient
from inference.models import DataFile

pytest_plugins = ["pytest_asyncio"]


@pytest.fixture
def csv_file() -> SimpleUploadedFile:
    """Fixture for test CSV file"""
    return SimpleUploadedFile("test.csv", b"col1,col2\n1,2\n3,4", content_type="text/csv")


@pytest.fixture
async def async_client():
    """Fixture for async client"""
    return AsyncClient()


@pytest.fixture(autouse=True)
async def _setup_teardown():
    """Automatic setup and teardown for all tests"""
    yield
    # Clean up after each test
    # pylint: disable=import-outside-toplevel
    from django.core.files.storage import default_storage

    # Convert sync queryset to async operation
    data_files: list[DataFile] = await sync_to_async(list)(DataFile.objects.all())  # type: ignore[call-arg]
    for data_file in data_files:
        if data_file.file:
            with contextlib.suppress(Exception):
                await sync_to_async(default_storage.delete)(data_file.file.name)
        await sync_to_async(data_file.delete)()
