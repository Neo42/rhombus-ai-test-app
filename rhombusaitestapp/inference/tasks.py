"""Tasks for the Rhombus AI Test App."""

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from celery import shared_task
from celery.app.task import Task

from .constants import ProcessingStatus
from .inference_engine import InferenceEngine
from .models import DataFile

# Define a type alias for JSON-serializable types
type JSONValue = dict[str, Any] | list[Any] | int | float | bool | str | None


def make_serializable(val: Any) -> JSONValue:
    """Convert non-serializable types to JSON-serializable format.

    Args:
        val: Any value that needs to be converted to JSON-serializable format

    Returns:
        A JSON-serializable value

    """
    match val:
        case dict():
            return {str(k): make_serializable(v) for k, v in val.items()}
        case list():
            return [make_serializable(v) for v in val]
        case np.integer():
            return int(val)
        case np.floating():
            return float(val)
        case np.bool_():
            return bool(val)
        case pd.Timestamp() | datetime():
            return val.strftime("%Y-%m-%d %H:%M:%S") if not pd.isnull(val) else None
        case pd.Timedelta() | np.timedelta64():
            return str(val) if not pd.isnull(val) else None
        case np.ndarray():
            return val.tolist()  # type: ignore[attr-defined]
        case complex():
            return str(val)
        case _:
            return str(val)


@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def process_file(self: Task, file_id: int) -> None:
    """Process file in background."""
    data_file = DataFile.objects.get(id=file_id)
    inference_engine = InferenceEngine()

    try:
        data_file.processing_status = ProcessingStatus.INFERRING
        data_file.save()

        # Process using inference engine
        df, processing_time = inference_engine.infer(data_file.file.path)

        # Convert types to JSON-serializable format
        inferred_types = {k: str(v) for k, v in df.dtypes.to_dict().items()}

        # Get sample data
        sample_data = df.head().to_dict(orient="records")

        # Convert any non-serializable types in sample data
        for record in sample_data:
            for key, value in record.items():
                record[key] = make_serializable(value)

        # Update results
        data_file.inferred_types = inferred_types
        data_file.sample_data = sample_data
        data_file.row_count = len(df)
        data_file.column_count = len(df.columns)
        data_file.processing_status = ProcessingStatus.INFERRED
        data_file.processing_time = processing_time
        data_file.save()

    except Exception as exc:
        data_file.processing_status = ProcessingStatus.INFERENCE_FAILED
        data_file.error_message = str(exc)
        data_file.save()
        raise self.retry(exc=exc) from exc
