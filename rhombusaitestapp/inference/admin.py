"""Admin for the Inference app."""

from django.contrib import admin

from .models import DataFile, DataType


@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    """Admin for the DataFile model."""

    list_display = (
        "original_filename",
        "processing_status",
        "uploaded_at",
        "row_count",
    )
    list_filter = ("processing_status",)
    search_fields = ("original_filename",)
    readonly_fields = (
        "processing_time",
        "error_message",
        "inferred_types",
        "sample_data",
    )


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
    """Admin for the DataType model."""

    list_display = ("display_name", "internal_name")
    search_fields = ("display_name", "internal_name")
