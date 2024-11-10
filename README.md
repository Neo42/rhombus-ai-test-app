# Data Type Inference API

A Django-based REST API for automatic data type inference from CSV and Excel files with real-time processing status updates.

## Tech Stack

### Core

- Python 3.13
- Django 5.1
- Django Ninja (FastAPI-inspired REST framework)
- Celery (Async task processing)
- Redis (Message broker)
- Polars & Pandas (Data processing)
- NumPy (Numerical operations)

### Development Tools

- Poetry (Dependency management)
- Pylint & Ruff (Linter + Formatter)
- Mypy (Static type checking)
- Pytest (Testing framework)

## Features

### File Processing

- Upload CSV and Excel files (up to 1GB)
- Automatic data type inference
- Sample data preview
- Real-time processing status updates
- Column type overrides
- Error handling and validation

### Data Type Inference

- Supports multiple data types:
  - Integer & Float
  - object
  - Boolean
  - Datetime & timedelta
  - Category
  - Complex Number
- Configurable sample size for type inference
- Handles missing values and data cleaning

## Next Step

- Improve data processing speed for large files (potentially using Polars instead of Pandas)
- Get all data instead of preview data
- Fix Github Actions

## Project Structure

```

rhombusaitestapp/
├── inference/
│ ├── api.py # API endpoints
│ ├── constants.py # Enums and constants
│ ├── models.py # Database models
│ ├── schemas.py # API schemas
│ ├── services.py # Business logic
│ ├── tasks.py # Celery tasks
│ └── inference_engine.py # Type inference logic
├── tests/
│ └── test_api.py # API tests (not complete)
└── rhombusaitestapp/
└── settings.py # Django settings

```

## Getting Started

### Prerequisites

- Python 3.13+
- Redis

```bash
brew install redis
```

- Homebrew, pipx & Poetry

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install pipx
pipx ensurepath
```

### Installation

1. Clone the repository and `cd` into it

2. Install dependencies:

```bash
poetry install
```

3. Apply migrations:

```bash
poetry run python manage.py migrate
```

4. Start Celery worker:

```bash
cd rhombusaitestapp
poetry run celery -A rhombusaitestapp worker --loglevel=info
```

5. Run development server:

```bash
# make sure you are in the root directory
poetry run python manage.py runserver
```

### Running Tests

```bash
# make sure you are in the root directory
poetry run pytest
```

### Code Quality

1. Run type checking:

```bash
# make sure you are in the root directory
poetry run mypy .
```

2. Run linter:

```bash
# make sure you are in the root directory
poetry run ruff check
```

3. Run formatter:

```bash
# make sure you are in the root directory
poetry run ruff format
```

## API Endpoints

### File Upload

```http
POST /api/upload
```

- Accepts CSV and Excel files
- Returns file ID and upload status

### Get File Status

```http
GET /api/files/{file_id}
```

- Returns processing status and inferred data types
- Includes sample data preview

### Override Column Type

```http
PATCH /api/files/{file_id}/columns/{column_name}
```

- Override inferred data type for specific column
- Returns updated column types

## Error Handling

The API uses standardized error responses:

```json
{
  "detail": "Error description",
  "code": "ERROR_CODE",
  "message": "User-friendly message"
}
```

Common error codes:

- VALIDATION_ERROR
- FILE_NOT_FOUND
- INVALID_FILE_TYPE
- PROCESSING_INCOMPLETE
- INTERNAL_ERROR
