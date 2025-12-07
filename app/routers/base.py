"""Reusable CRUD router factory."""
from typing import Type, List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from pydantic import BaseModel, create_model
from app.db import get_db


def model_to_dict(model_instance) -> Dict[str, Any]:
    """Convert SQLAlchemy model instance to dictionary."""
    return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}


def create_crud_router(
    model_class: Type,
    table_name: str,
    prefix: str,
    tags: Optional[List[str]] = None
) -> APIRouter:
    """
    Create a CRUD router for a given SQLAlchemy model.
    
    Args:
        model_class: The SQLAlchemy model class
        table_name: Name of the database table
        prefix: URL prefix for the router (e.g., "/api/enrollments")
        tags: Optional tags for OpenAPI documentation
    
    Returns:
        APIRouter with CRUD endpoints
    """
    router = APIRouter(prefix=prefix, tags=tags or [table_name])
    
    # Get primary key column
    mapper = inspect(model_class)
    pk_column = None
    for col in mapper.columns:
        if col.primary_key:
            pk_column = col
            break
    
    if pk_column is None:
        raise ValueError(f"No primary key found for {table_name}")
    
    pk_name = pk_column.name
    # Get Python type for primary key
    try:
        pk_type = pk_column.type.python_type
    except (AttributeError, NotImplementedError):
        # Fallback to int for unknown types
        pk_type = int
    
    # Create Pydantic models dynamically
    fields = {}
    for col in mapper.columns:
        try:
            col_type = col.type.python_type
        except (AttributeError, NotImplementedError):
            # Fallback to str for unknown types
            col_type = str
        # Handle optional columns
        if col.nullable:
            fields[col.name] = (Optional[col_type], None)
        else:
            fields[col.name] = (col_type, ...)
    
    # Create schemas
    CreateSchema = create_model(f"{model_class.__name__}Create", **fields)
    UpdateSchema = create_model(f"{model_class.__name__}Update", **{k: (v[0], None) for k, v in fields.items()})
    ResponseSchema = create_model(f"{model_class.__name__}Response", **fields)
    
    # GET all
    @router.get("/", response_model=List[Dict[str, Any]])
    def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        """Get all records."""
        try:
            items = db.query(model_class).offset(skip).limit(limit).all()
            return [model_to_dict(row) for row in items]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching {table_name}: {str(e)}"
            )
    
    # GET by id
    @router.get("/{item_id}", response_model=Dict[str, Any])
    def get_by_id(item_id: pk_type, db: Session = Depends(get_db)):
        """Get a record by ID."""
        try:
            item = db.query(model_class).filter(getattr(model_class, pk_name) == item_id).first()
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{table_name} with id {item_id} not found"
                )
            return model_to_dict(item)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching {table_name}: {str(e)}"
            )
    
    # POST
    @router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
    def create(item: CreateSchema, db: Session = Depends(get_db)):
        """Create a new record."""
        try:
            item_dict = item.dict(exclude_unset=True)
            db_item = model_class(**item_dict)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return model_to_dict(db_item)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating {table_name}: {str(e)}"
            )
    
    # PUT
    @router.put("/{item_id}", response_model=Dict[str, Any])
    def update(item_id: pk_type, item: UpdateSchema, db: Session = Depends(get_db)):
        """Update a record by ID."""
        try:
            db_item = db.query(model_class).filter(getattr(model_class, pk_name) == item_id).first()
            if not db_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{table_name} with id {item_id} not found"
                )
            
            item_dict = item.dict(exclude_unset=True)
            for key, value in item_dict.items():
                setattr(db_item, key, value)
            
            db.commit()
            db.refresh(db_item)
            return model_to_dict(db_item)
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error updating {table_name}: {str(e)}"
            )
    
    # DELETE
    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete(item_id: pk_type, db: Session = Depends(get_db)):
        """Delete a record by ID."""
        try:
            db_item = db.query(model_class).filter(getattr(model_class, pk_name) == item_id).first()
            if not db_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{table_name} with id {item_id} not found"
                )
            
            db.delete(db_item)
            db.commit()
            return None
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting {table_name}: {str(e)}"
            )
    
    return router

