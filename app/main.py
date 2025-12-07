from dotenv import load_dotenv
load_dotenv()

"""FastAPI main application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    enrollments,
    subjects,
    assessments_eol,
    assessments_fa,
    assessments_sa,
    assessment_weights,
    users_table,
    myp_grade_boundaries,
    dp_grade_boundaries,
)

# Create FastAPI app
app = FastAPI(
    title="SLP API",
    description="FastAPI application for SLP database",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(enrollments.router)
app.include_router(subjects.router)
app.include_router(assessments_eol.router)
app.include_router(assessments_fa.router)
app.include_router(assessments_sa.router)
app.include_router(assessment_weights.router)
app.include_router(users_table.router)
app.include_router(myp_grade_boundaries.router)
app.include_router(dp_grade_boundaries.router)


@app.get("/")
def root(request: Request):
    """Root endpoint returning all API endpoint URLs."""
    base_url = str(request.base_url).rstrip("/")
    return {
        "enrollments": f"{base_url}/api/enrollments/",
        "subjects": f"{base_url}/api/subjects/",
        "assessments/eol": f"{base_url}/api/assessments/eol/",
        "assessments/fa": f"{base_url}/api/assessments/fa/",
        "assessments/sa": f"{base_url}/api/assessments/sa/",
        "assessment-weights": f"{base_url}/api/assessment-weights/",
        "users-table": f"{base_url}/api/users-table/",
        "myp-grade-boundaries": f"{base_url}/api/myp-grade-boundaries/",
        "dp-grade-boundaries": f"{base_url}/api/dp-grade-boundaries/"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

