"""Assessments FA router."""
from fastapi import APIRouter
from app.db import get_model_by_table_name, TABLE_MAPPING
from app.routers.base import create_crud_router

# Get the model
model = get_model_by_table_name(TABLE_MAPPING["assessments_fa"])

# Create router
router = create_crud_router(
    model_class=model,
    table_name=TABLE_MAPPING["assessments_fa"],
    prefix="/api/assessments/fa",
    tags=["assessments", "fa"]
)

