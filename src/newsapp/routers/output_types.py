from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import OutputType

router = APIRouter(prefix="/output-types", tags=["output-types"])

class OutputTypeIn(BaseModel):
    name: str
    description: Optional[str] = None
    ai_instructions: Optional[str] = None
    expected_schema: Optional[dict] = None
    dashboard_rules: Optional[dict] = None

class OutputTypeOut(OutputTypeIn):
    id: int
    class Config: 
        from_attributes = True

@router.get("", response_model=List[OutputTypeOut])
def list_types(db: Session = Depends(get_db)):
    return db.query(OutputType).order_by(OutputType.name.asc()).all()

@router.post("", response_model=OutputTypeOut, status_code=201)
def create_type(data: OutputTypeIn, db: Session = Depends(get_db)):
    if db.query(OutputType).filter(OutputType.name == data.name).first():
        raise HTTPException(409, "name already exists")
    obj = OutputType(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{oid}", response_model=OutputTypeOut)
def get_type(oid: int, db: Session = Depends(get_db)):
    obj = db.get(OutputType, oid)
    if not obj:
        raise HTTPException(404, "not found")
    return obj

@router.put("/{oid}", response_model=OutputTypeOut)
def update_type(oid: int, data: OutputTypeIn, db: Session = Depends(get_db)):
    obj = db.get(OutputType, oid)
    if not obj:
        raise HTTPException(404, "not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{oid}")
def delete_type(oid: int, db: Session = Depends(get_db)):
    obj = db.get(OutputType, oid)
    if not obj:
        raise HTTPException(404, "not found")
    db.delete(obj)
    db.commit()
    return {"status": "deleted", "id": oid}
