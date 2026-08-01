"""
Thin entry-point so you can run:
    uvicorn main:app --reload
from the backend/ directory.
"""
from app.main import app  # noqa: F401
