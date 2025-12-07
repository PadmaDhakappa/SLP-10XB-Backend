import os
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, Session

# Optional pgvector import with safety
try:
    import pgvector
except ImportError:
    pgvector = None

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Automap base
Base = automap_base()

# Reflect all tables
Base.prepare(autoload_with=engine)

# Table name mapping: endpoint path → database table name
TABLE_MAPPING = {
    "enrollments": "enrollments",
    "subjects": "subjects",
    "assessments_eol": "assessments_eol",
    "assessments_fa": "assessments_fa",
    "assessments_sa": "assessments_sa",
    "assessment_weights": "assessment_weights",
    "users_table": "users_table",
    "myp_grade_boundaries": "myp_grade_boundaries",
    "dp_grade_boundaries": "dp_grade_boundaries",
}

# Get models by table name
def get_model_by_table_name(table_name: str):
    """Get the automapped model class by table name."""
    for class_name, model_class in Base.classes.items():
        if hasattr(model_class, "__table__") and model_class.__table__.name == table_name:
            return model_class
    raise ValueError(f"Table '{table_name}' not found in database")

# Dependency for database sessions
def get_db():
    """Dependency function for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

