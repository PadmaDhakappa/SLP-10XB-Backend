"""Subjects router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_model_by_table_name, TABLE_MAPPING, get_db
from app.routers.base import create_crud_router

# Get the model
model = get_model_by_table_name(TABLE_MAPPING["subjects"])

# Create base CRUD router
router = create_crud_router(
    model_class=model,
    table_name=TABLE_MAPPING["subjects"],
    prefix="/api/subjects",
    tags=["subjects"]
)

# -----------------------------
# Custom filtering endpoint
# -----------------------------
@router.get("/filter", tags=["subjects"])
def filter_subjects(
    enrollment_id: str,
    subject: str,
    db: Session = Depends(get_db)
):
    """Return a subject record matching enrollment_id + subject."""
    record = (
        db.query(model)
        .filter(
            model.enrollment_id == enrollment_id,
            model.subject == subject
        )
        .all()
    )
    return record

