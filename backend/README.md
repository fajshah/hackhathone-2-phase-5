# Backend Setup

This directory contains the backend components for the Phase 5 project.

## Requirements

The backend is built with Python and uses Flask as the web framework. All required packages are listed in `requirements.txt`.

## Installation

To install the backend dependencies, run:

```bash
pip install -r requirements.txt
```

### Notes for Windows Users

If you encounter issues installing `psycopg2-binary`, try one of these approaches:

1. Install from conda-forge: `conda install psycopg2`
2. Use the pre-compiled wheel: `pip install --only-binary=psycopg2-binary psycopg2-binary`
3. Use SQLite instead (comes with Python) by commenting out the psycopg2-binary line in requirements.txt

## Verification

To verify that all packages are installed correctly, run:

```bash
python test_installation.py
```

## Key Dependencies

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-SQLAlchemy**: Flask extension for SQLAlchemy
- **Alembic**: Database migration tool
- **Flask-Migrate**: Flask extension for Alembic
- **Flask-CORS**: Cross-origin resource sharing support
- **Flask-Login**: User session management
- **Marshmallow**: Object serialization/deserialization
- **Celery**: Distributed task queue
- **Redis**: In-memory data store (used with Celery)
- **Pytest**: Testing framework
- **Structlog**: Structured logging
- **Python-dotenv**: Environment variable management
- **Requests**: HTTP library
- **Bcrypt**: Password hashing