# Generated by Django 5.1.2 on 2024-11-02 03:36

import django.core.validators
from django.db import migrations, models

from inference.constants import ProcessingStatus


class Migration(migrations.Migration):

    dependencies = [
        ("inference", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="uploads/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["csv", "xlsx", "xls"]
                            )
                        ],
                    ),
                ),
                ("original_filename", models.CharField(max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "processing_status",
                    models.CharField(
                        choices=ProcessingStatus.choices,
                        default=ProcessingStatus.IDLE.value,
                        max_length=20,
                    ),
                ),
                ("processing_time", models.FloatField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("inferred_types", models.JSONField(blank=True, null=True)),
                ("overridden_types", models.JSONField(blank=True, null=True)),
                ("sample_data", models.JSONField(blank=True, null=True)),
                ("row_count", models.IntegerField(blank=True, null=True)),
                ("column_count", models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="DataType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("internal_name", models.CharField(max_length=50)),
                ("display_name", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="employee",
            name="department",
        ),
        migrations.DeleteModel(
            name="Department",
        ),
        migrations.DeleteModel(
            name="Employee",
        ),
    ]
