"""Inference engine for the Rhombus AI Test App."""

import re
import time
from pathlib import Path
from typing import ClassVar

import numpy as np
import pandas as pd
import polars as pl


class InferenceEngine:
    """Engine for inferring and converting data types from CSV or Excel files."""

    # Move patterns to class attributes
    DATE_PATTERNS: ClassVar[list[str]] = [
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+$",
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$",
        r"^\d{2}/\d{2}/\d{4}$",
        r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$",
        r"^\d{4}-\d{2}-\d{2}$",
    ]

    TIMEDELTA_PATTERNS: ClassVar[list[str]] = [
        r"^[-]?\d+\s*days?$",
        r"^[-]?\d+\s*d$",
        r"^(\d+):(\d{2})(:\d{2})?(\.\d+)?$",
        r"^[-]?\d+\s*hours?$",
        r"^[-]?\d+\s*h$",
        r"^[-]?\d+\s*minutes?$",
        r"^[-]?\d+\s*m$",
        r"^[-]?\d+\s*seconds?$",
        r"^[-]?\d+\s*s$",
        r"^[-]?\d+\s*days?\s*[+-]?\s*\d{2}:\d{2}(:\d{2})?(\.\d+)?$",
    ]

    @staticmethod
    def _get_boolean_mapping() -> dict:
        """Get boolean mapping dictionary."""
        true_values = ["true", "yes", "y", "1", "t", True, 1]
        false_values = ["false", "no", "n", "0", "f", False, 0]
        mapping = {str(val).lower(): True for val in true_values}
        mapping.update({str(val).lower(): False for val in false_values})
        return mapping

    def infer(self: "InferenceEngine", file_path: str, sample_size: int = 1000) -> tuple[pd.DataFrame, float]:
        """Infer and convert data types from CSV or Excel files."""
        start_time = time.time()

        try:
            df = self._read_file(file_path)
            inferred_dtypes = {}
            boolean_mapping = self._get_boolean_mapping()

            for col in df.columns:
                df[col] = self._clean_column(df[col])

                if df[col].dtype == "object":
                    df[col] = df[col].astype(str).str.strip()
                    df[col], inferred_dtypes[col] = self._infer_column_type(df[col], boolean_mapping, sample_size)

            processing_time = time.time() - start_time

        except Exception as e:
            msg = f"Error reading file: {e!s}"
            raise ValueError(msg) from e
        return df, processing_time

    def _clean_column(self: "InferenceEngine", series: pd.Series) -> pd.Series:
        """Clean column data by replacing common null values."""
        return series.replace(
            ["None", "NaN", "null", "Null", "not available", "Not Available"],
            np.nan,
        )

    def _infer_column_type(
        self: "InferenceEngine",
        series: pd.Series,
        boolean_mapping: dict,
        sample_size: int,
    ) -> tuple[pd.Series, str]:
        """Infer the type of a column."""
        for infer_func in [
            lambda s: self._infer_boolean(s, boolean_mapping),
            self._infer_complex,
            self._infer_numeric,
            lambda s: self._infer_datetime(s, self.DATE_PATTERNS, sample_size),
            lambda s: self._infer_timedelta(s, self.TIMEDELTA_PATTERNS),
        ]:
            series, dtype = infer_func(series)
            if dtype:
                return series, dtype

        # If no other type matched, try categorical
        return self._infer_categorical(series)

    def _read_file(self: "InferenceEngine", file_path: str) -> pd.DataFrame:
        """Read file and convert to pandas DataFrame."""
        file_extension = Path(file_path).suffix.lower()
        if file_extension == ".csv":
            polars_df = pl.read_csv(file_path, raise_if_empty=False)
        elif file_extension in [".xlsx", ".xls"]:
            polars_df = pl.read_excel(file_path, raise_if_empty=False)
        else:
            msg = f"Unsupported file format: {file_extension}"
            raise ValueError(msg)
        return polars_df.to_pandas()

    def _infer_boolean(
        self: "InferenceEngine", series: pd.Series, boolean_mapping: dict
    ) -> tuple[pd.Series, str | None]:
        """Infer boolean data type."""
        if series.dropna().str.lower().isin(boolean_mapping.keys()).all():
            return series.str.lower().map(boolean_mapping).astype("bool"), "bool"
        return series, None

    def _infer_complex(self: "InferenceEngine", series: pd.Series) -> tuple[pd.Series, str | None]:
        """Infer complex number data type."""
        complex_match = series.apply(
            lambda x: isinstance(x, str) and re.match(r"^\(?-?\d+(\.\d+)?[+-]\d+(\.\d+)?j\)?$", x)
        )
        if complex_match.any():
            series = series.apply(lambda x: (complex(x) if isinstance(x, str) and ("+" in x or "-" in x) else np.nan))
            if series.apply(lambda x: isinstance(x, complex)).any():
                return series, "complex128"
        return series, None

    def _infer_numeric(self: "InferenceEngine", series: pd.Series) -> tuple[pd.Series, str | None]:
        """Infer numeric data type."""
        numeric_col = pd.to_numeric(series, errors="coerce")
        if numeric_col.notna().sum() > 0:
            dtype = "float64" if numeric_col.hasnans else "int64"
            return numeric_col, dtype
        return series, None

    def _infer_datetime(
        self: "InferenceEngine",
        series: pd.Series,
        date_patterns: list[str],
        sample_size: int,
    ) -> tuple[pd.Series, str | None]:
        """Infer datetime data type."""
        sample = series.dropna().astype(str).sample(n=min(sample_size, len(series.dropna())), random_state=1)
        date_matches = sample.apply(lambda x: any(re.match(pattern, str(x)) for pattern in date_patterns))
        if date_matches.mean() > 0.5:
            try:
                # Convert to datetime using Polars first for better performance
                temp_df = pl.from_pandas(pd.DataFrame({series.name: series}))
                temp_df = temp_df.with_columns(pl.col(series.name).str.to_datetime(format=None, strict=False))
                series = temp_df[series.name].to_pandas()

                # Fallback to pandas if needed
                if series.dtype != "datetime64[ns]":
                    series = pd.to_datetime(series, format="%Y-%m-%d %H:%M:%S.%f")
            except (
                pl.ComputeError,
                pl.SchemaError,
                ValueError,
                pd.errors.ParserError,
            ):
                # If conversion fails, try pandas with flexible parsing
                series = pd.to_datetime(series, errors="coerce")
                if series.notna().sum() > 0:
                    return series, "datetime64[ns]"
            else:
                return series, "datetime64[ns]"
        return series, None

    def _infer_timedelta(
        self: "InferenceEngine", series: pd.Series, timedelta_patterns: list[str]
    ) -> tuple[pd.Series, str | None]:
        """Infer timedelta data type."""
        if (
            series.dropna()
            .astype(str)
            .apply(lambda x: any(re.match(p, x.strip().lower()) for p in timedelta_patterns))
            .any()
        ):
            return series.apply(self._parse_timedelta), "timedelta64[ns]"
        return series, None

    def _infer_categorical(self: "InferenceEngine", series: pd.Series) -> tuple[pd.Series, str]:
        """Infer categorical or object data type."""
        unique_ratio = series.nunique(dropna=True) / len(series)
        if unique_ratio < 0.5:
            return series.astype("category"), "category"
        return series.astype("object"), "object"

    def _parse_timedelta(self: "InferenceEngine", value: str) -> pd.Timedelta:
        """Parse a timedelta string in formats like '-428 days +19:23:03.487674'."""
        days_match = re.search(r"([-]?\d+)\s*days?", value)
        time_match = re.search(r"(\d{1,2}):(\d{2})(:\d{2}(\.\d+)?)?", value)

        days = pd.Timedelta(days=int(days_match.group(1))) if days_match else pd.Timedelta(0)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            seconds = float(time_match.group(3)[1:]) if time_match.group(3) else 0
            time_delta = pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
        else:
            time_delta = pd.Timedelta(0)

        return days + time_delta
