"""Re-export automapped models from db module."""
from app.db import Base, get_model_by_table_name, TABLE_MAPPING

__all__ = ["Base", "get_model_by_table_name", "TABLE_MAPPING"]

