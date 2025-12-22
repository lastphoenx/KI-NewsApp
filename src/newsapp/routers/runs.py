from typing import Optional, List, Any
from datetime import datetime
import asyncio
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Template, SearchRun, OutputType
from ..config import DEFAULTS
from ..utils.llm_stage import run_llm_on_passages, LLMError

router = APIRouter(prefix="/runs", tags=["runs"])

class RunCreate(BaseModel):
    template_id: int
    extra_urls: Optional[List[str]] = None
    # NEU: KI-Auswahl pro Run (überschreibt Template-Defaults)
    ai_provider: Optional[str] = None     # openai|anthropic|mistral
    ai_model: Optional[str] = None
    ai_temperature: Optional[float] = None
    use_ai: Optional[bool] = True         # False = kein LLM-Call

class RunResultIn(BaseModel):
    relevance_score: Optional[float] = None
    summary: Optional[Any] = None
    changes: Optional[Any] = None
    actions: Optional[Any] = None
    risks: Optional[Any] = None
    findings_per_page: Optional[Any] = None
    evidence_summary: Optional[Any] = None
    raw_response: Optional[Any] = None

class RunOut(BaseModel):
    id: int
    template_id: int
    status: str
    relevance_score: Optional[float] = None
    summary: Optional[Any] = None
    changes: Optional[Any] = None
    actions: Optional[Any] = None
    risks: Optional[Any] = None
    findings_per_page: Optional[Any] = None
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    class Config:
        from_attributes = True

@router.get("", response_model=List[RunOut])
def list_runs(db: Session = Depends(get_db)):
    return db.query(SearchRun).order_by(SearchRun.created_at.desc()).limit(100).all()

@router.get("/{rid}", response_model=RunOut)
def get_run(rid: int, db: Session = Depends(get_db)):
    r = db.query(SearchRun).get(rid)
    if not r:
        raise HTTPException(404, "run not found")
    return r

@router.post("", response_model=RunOut, status_code=201)
def start_run(data: RunCreate, db: Session = Depends(get_db)):
    """
    Startet eine neue Analyse:
    1. Fetcht URLs (Mock: generiert Dummy-Text)
    2. Scored Seiten nach Keywords
    3. Optional: LLM-Analyse mit gewähltem Provider
    """
    t = db.query(Template).get(data.template_id)
    if not t:
        raise HTTPException(404, "template not found")

    # URLs zusammenstellen: urls_csv hat Vorrang, dann trusted_urls als Fallback
    seed_urls = t.urls_list() or (t.trusted_urls or [])
    if data.extra_urls:
        seed_urls = list(dict.fromkeys(seed_urls + data.extra_urls))
    
    if not seed_urls:
        raise HTTPException(400, "Keine URLs vorhanden (weder im Template noch extra_urls)")

    # === PHASE 1: Fetching & Scoring ===
    from ..utils.fetcher import fetch_multiple
    
    keywords = t.keywords_list()
    findings = []
    page_scores = []
    
    # URLs parallel fetchen
    fetched_pages = asyncio.run(fetch_multiple(seed_urls[:10], max_concurrent=3))
    
    for page in fetched_pages:
        url = page["url"]
        text = page.get("text", "")
        
        # Bei Fehler: Skip oder niedrigen Score
        if page.get("error") or not text:
            findings.append({
                "url": url,
                "status": page["status"],
                "error": page.get("error", "Kein Text extrahiert"),
                "page_relevance": 0.0,
                "key_findings": [],
                "keyword_details": {}
            })
            page_scores.append(0.0)
            continue
        
        # Keyword-Scoring
        text_lower = text.lower()
        score = 0.0
        keyword_matches = {}
        
        for kw in keywords:
            count = text_lower.count(kw.lower())
            if count > 0:
                # Score: 1 Punkt pro Vorkommen, max 5 Punkte pro Keyword
                kw_score = min(count, 5)
                score += kw_score
                keyword_matches[kw] = count
        
        # Max 10 Punkte
        score = min(score, 10.0)
        page_scores.append(score)
        
        # Key Findings: Extrahiere Sätze mit Keywords
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        key_finds = []
        for sentence in sentences:
            if any(kw.lower() in sentence.lower() for kw in keywords):
                key_finds.append(sentence[:200])  # Max 200 Zeichen pro Finding
                if len(key_finds) >= 5:  # Max 5 Findings
                    break
        
        findings.append({
            "url": url,
            "status": page["status"],
            "content_type": page.get("content_type"),
            "title": page.get("title", ""),
            "page_relevance": round(score, 1),
            "key_findings": key_finds,
            "keyword_details": keyword_matches,
        })
    
    # Gesamt-Relevanz berechnen
    def aggregate_scores(scores):
        if not scores:
            return 0.0
        best = sorted(scores, reverse=True)[:3]
        rest = scores[len(best):]
        w = (sum(best) * 0.7 + sum(rest) * 0.3) / (len(best) * 0.7 + (len(rest) or 1) * 0.3)
        return round(w, 1)
    
    relevance = aggregate_scores(page_scores)

    # === PHASE 2: LLM-Analyse (Optional) ===
    llm_payload = {}
    
    if data.use_ai:
        # Provider/Model bestimmen (Priorität: Run > Template > .env)
        provider = (data.ai_provider or t.ai_provider or DEFAULTS["provider"]).lower()
        model = data.ai_model or t.ai_model or DEFAULTS["model"]
        temp = data.ai_temperature if data.ai_temperature is not None else (
            t.ai_temperature if t.ai_temperature is not None else DEFAULTS["temperature"]
        )
        
        # API-Key prüfen
        from ..config import get_api_keys
        api_keys = get_api_keys()
        key_map = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "mistral": "MISTRAL_API_KEY"}
        
        provider_key = api_keys.get(provider)
        if not provider_key or len(provider_key.strip()) < 10:
            raise HTTPException(
                400, 
                f"API-Key für '{provider}' fehlt oder ungültig! Bitte in .env oder Windows-Umgebungsvariable setzen: {key_map.get(provider, 'UNKNOWN')}"
            )
        
        # Passagen-Text: Top-N Seiten nach Score
        top_pages = sorted(findings, key=lambda x: x["page_relevance"], reverse=True)[:5]
        passages_text = ""
        for p in top_pages:
            passages_text += f"[URL] {p['url']}\n"
            for k in p["key_findings"]:
                passages_text += f"- {k}\n"
            passages_text += "\n"
        
        # Output-Typen dieses Templates
        ots: List[OutputType] = t.output_types or []
        ot_dicts = []
        for ot in ots:
            ot_dicts.append({
                "name": ot.name,
                "ai_instructions": ot.ai_instructions,
                "expected_schema": ot.expected_schema,
                "dashboard_rules": ot.dashboard_rules,
            })
        
        # LLM-Call (async in sync Route via asyncio.run)
        try:
            llm_payload = asyncio.run(
                run_llm_on_passages(
                    provider=provider,
                    model=model,
                    persona=t.persona,
                    assignment=t.assignment,
                    output_types=ot_dicts,
                    passages_text=passages_text,
                    temperature=temp,
                )
            )
            
            # ===== DEBUG LOGGING =====
            import logging
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            logger.info(f"=== LLM DEBUG === Provider: {provider}, Model: {model}")
            logger.info(f"llm_payload type: {type(llm_payload)}")
            logger.info(f"llm_payload keys: {llm_payload.keys() if isinstance(llm_payload, dict) else 'NOT A DICT'}")
            logger.info(f"llm_payload: {llm_payload}")
            
            # Validierung & Fallback: Stelle sicher dass changes/actions/risks konsistent sind
            changes = llm_payload.get("changes") or []
            actions = llm_payload.get("actions") or []
            risks = llm_payload.get("risks") or []
            logger.info(f"After extraction - changes: {len(changes)}, actions: {len(actions)}, risks: {len(risks)}")
            
            # Wenn changes vorhanden aber actions/risks fehlen → generiere Platzhalter
            if changes and (not actions or not risks):
                num_changes = len(changes)
                
                if not actions or len(actions) < num_changes:
                    # Fülle fehlende Actions auf
                    for i in range(len(actions), num_changes):
                        actions.append({
                            "action": f"Analyse durchführen: {changes[i].get('topic', 'Unbekannt')}",
                            "priority": changes[i].get("impact", "medium"),
                            "deadline": changes[i].get("effective_date", "TBD"),
                            "effort": "TBD",
                            "owner_role": "Cash Management Team",
                            "reason": f"Reaktion auf Change: {changes[i].get('description', '')}",
                            "dependencies": []
                        })
                    llm_payload["actions"] = actions
                
                if not risks or len(risks) < num_changes:
                    # Fülle fehlende Risks auf
                    for i in range(len(risks), num_changes):
                        risks.append({
                            "risk": f"Nichtumsetzung: {changes[i].get('topic', 'Unbekannt')}",
                            "area": "Business",
                            "severity": changes[i].get("impact", "medium"),
                            "likelihood": "medium",
                            "consequence": f"Verpasste Deadline oder Compliance-Issue",
                            "mitigation": "Rechtzeitige Planung und Umsetzung",
                            "detection": "Regelmäßige Überprüfung"
                        })
                    llm_payload["risks"] = risks
            
            # Wenn gar nichts vorhanden → generiere mindestens 1 Dummy-Set
            if not changes:
                llm_payload["changes"] = [{
                    "topic": "Keine Changes erkannt",
                    "description": "LLM hat keine spezifischen Änderungen identifiziert",
                    "effective_date": "TBD",
                    "impact": "low",
                    "affected_interfaces": [],
                    "spec_reference": "N/A",
                    "change_type": "operational"
                }]
                llm_payload["actions"] = [{
                    "action": "Manuelle Review der Findings durchführen",
                    "priority": "low",
                    "deadline": "TBD",
                    "effort": "1 Tag",
                    "owner_role": "Team Lead",
                    "reason": "Automatische Analyse unvollständig",
                    "dependencies": []
                }]
                llm_payload["risks"] = [{
                    "risk": "Unvollständige Analyse",
                    "area": "Ops",
                    "severity": "low",
                    "likelihood": "low",
                    "consequence": "Möglicherweise übersehene Änderungen",
                    "mitigation": "Manuelle Nachkontrolle empfohlen",
                    "detection": "Review durch Experten"
                }]
                
        except LLMError as e:
            llm_payload = {"_llm_error": str(e)}
        except Exception as e:
            llm_payload = {"_error": str(e)}

    # === PHASE 3: SearchRun speichern ===
    r = SearchRun(
        template_id=t.id,
        status="completed",
        seed_urls=seed_urls,
        keywords_used={"keywords": keywords, "aliases": t.keyword_aliases or {}},
        relevance_score=relevance,
        findings_per_page={"items": findings},
        summary={
            "pages_analyzed": len(seed_urls),
            "avg_page_score": round(sum(page_scores) / len(page_scores), 2) if page_scores else 0.0,
            "ai_provider": data.ai_provider or t.ai_provider or DEFAULTS["provider"] if data.use_ai else None,
            "ai_model": data.ai_model or t.ai_model or DEFAULTS["model"] if data.use_ai else None,
        },
        # LLM-Felder (werden direkt gemappt, wenn vorhanden)
        changes=llm_payload.get("changes"),
        actions=llm_payload.get("actions"),
        risks=llm_payload.get("risks"),
        finished_at=datetime.utcnow(),
    )
    
    db.add(r)
    db.commit()
    db.refresh(r)
    
    return r

@router.put("/{rid}/result", response_model=RunOut)
def attach_result(rid: int, data: RunResultIn, db: Session = Depends(get_db)):
    r = db.get(SearchRun, rid)
    if not r:
        raise HTTPException(404, "run not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    if r.status != "failed":
        r.status = "completed"
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.delete("/{rid}")
def delete_run(rid: int, db: Session = Depends(get_db)):
    r = db.query(SearchRun).get(rid)
    if not r:
        raise HTTPException(404, "run not found")
    db.delete(r); db.commit()
    return {"status": "deleted", "id": rid}
