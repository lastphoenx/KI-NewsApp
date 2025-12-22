from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Template, OutputType

router = APIRouter(prefix="/templates", tags=["templates"])

class TemplateIn(BaseModel):
    name: str
    urls_csv: Optional[str] = None
    keywords_csv: Optional[str] = None
    persona: Optional[str] = None
    assignment: Optional[str] = None
    trusted_urls: Optional[List[str]] = None
    allowed_domains: Optional[List[str]] = None
    keyword_aliases: Optional[dict] = None
    scoring_rules: Optional[dict] = None
    output_type_ids: Optional[List[int]] = None  # Auswahl per IDs
    # NEU: KI-Konfiguration
    ai_provider: Optional[str] = None        # openai|anthropic|mistral
    ai_model: Optional[str] = None          # z.B. gpt-4o-mini, claude-3-5-sonnet-latest
    ai_temperature: Optional[float] = None  # 0.0-1.0

class TemplateOut(TemplateIn):
    id: int
    class Config:
        from_attributes = True

@router.get("", response_model=List[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return db.query(Template).order_by(Template.name.asc()).all()

@router.get("/{tid}", response_model=TemplateOut)
def get_template(tid: int, db: Session = Depends(get_db)):
    obj = db.query(Template).get(tid)
    if not obj:
        raise HTTPException(404, "template not found")
    return obj

@router.post("", response_model=TemplateOut, status_code=201)
def create_template(data: TemplateIn, db: Session = Depends(get_db)):
    if db.query(Template).filter(Template.name == data.name).first():
        raise HTTPException(409, "template name already exists")
    
    output_type_ids = (data.output_type_ids or []).copy()
    payload = data.model_dump()
    payload.pop("output_type_ids", None)
    
    obj = Template(**payload)
    if output_type_ids:
        types = db.query(OutputType).filter(OutputType.id.in_(output_type_ids)).all()
        obj.output_types = types
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{tid}", response_model=TemplateOut)
def update_template(tid: int, data: TemplateIn, db: Session = Depends(get_db)):
    obj = db.query(Template).get(tid)
    if not obj:
        raise HTTPException(404, "template not found")
    
    output_type_ids = (data.output_type_ids or []).copy()
    payload = data.model_dump()
    payload.pop("output_type_ids", None)
    
    for k, v in payload.items():
        setattr(obj, k, v)
    
    if data.output_type_ids is not None:
        types = db.query(OutputType).filter(OutputType.id.in_(output_type_ids)).all()
        obj.output_types = types
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{tid}")
def delete_template(tid: int, db: Session = Depends(get_db)):
    obj = db.query(Template).get(tid)
    if not obj:
        raise HTTPException(404, "template not found")
    db.delete(obj); db.commit()
    return {"status": "deleted", "id": tid}
