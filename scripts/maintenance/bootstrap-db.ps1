# bootstrap-db.ps1
$root = $PSScriptRoot

# --- venv + deps ---
if (-not (Test-Path "$root\.venv")) {
  python -m venv "$root\.venv"
}
& "$root\.venv\Scripts\Activate.ps1"
if (Test-Path "$root\requirements.txt") {
  pip install -r "$root\requirements.txt"
}

# --- models.py (Templates, Runs, Evidence) ---
@'
from __future__ import annotations
from typing import Optional, Any
from sqlalchemy import String, Integer, Text, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import Base

# ------------------------------
# Templates (Such-Templates)
# ------------------------------
class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # a) Stammdaten
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)

    # b) Einfache Eingabe-Felder (menschlich pflegbar)
    urls_csv: Mapped[Optional[str]] = mapped_column(Text, nullable=True)       # Komma-getrennte URLs
    keywords_csv: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # Komma-getrennte Stichworte
    persona: Mapped[Optional[str]] = mapped_column(Text, nullable=True)        # Funktionsbeschreibung ("Du bist ...")
    assignment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)     # Auftrag/Instruktion

    # c) Strukturierte Profifelder (optional, für spätere Power-User)
    trusted_urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)      # ["https://..."]
    allowed_domains: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)   # ["six-group.com"]
    keyword_aliases: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)   # {"ISO20022": ["iso 20022", ...]}
    output_types: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)      # ["summary","changes","action","risk","page_analysis"]
    scoring_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)     # {"weights":{"high":3,"med":2,"low":1}, ...}

    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Any] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    runs: Mapped[list["SearchRun"]] = relationship(back_populates="template", cascade="all, delete-orphan")

    # Hilfsmethoden für CSV -> Liste
    def urls_list(self) -> list[str]:
        return [u.strip() for u in (self.urls_csv or "").split(",") if u.strip()]

    def keywords_list(self) -> list[str]:
        return [k.strip() for k in (self.keywords_csv or "").split(",") if k.strip()]

# ------------------------------
# SearchRun (konkrete Analyse)
# ------------------------------
class SearchRun(Base):
    __tablename__ = "search_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id", ondelete="CASCADE"), index=True)

    status: Mapped[str] = mapped_column(String(32), default="running")  # running|completed|failed
    provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)     # z.B. openai
    model: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)        # z.B. gpt-4.x
    token_usage: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)       # {"prompt":..,"completion":..}

    # Nachvollziehbarkeit der Eingaben
    seed_urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)         # tatsächlich verwendete URLs
    keywords_used: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)     # Keywords + Aliasse

    # Ergebnisse (strukturiert)
    relevance_score: Mapped[Optional[Float]] = mapped_column(Float, nullable=True) # 0..10
    summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)           # ["bullet", ...]
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)           # [{topic, description, effective_date, impact, affected_systems}]
    actions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)           # [{action, priority, deadline, effort, reason}]
    risks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)             # [{risk, severity, likelihood, mitigation}]
    findings_per_page: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # [{url, page_relevance, key_findings, deadlines}]

    # Evidenz & Rohantwort (optional)
    evidence_summary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Passagen/Belege
    raw_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)      # LLM-Roh-JSON

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), nullable=True)

    template: Mapped["Template"] = relationship(back_populates="runs")
    pages: Mapped[list["EvidencePage"]] = relationship(back_populates="run", cascade="all, delete-orphan")

# ------------------------------
# EvidencePage (optionale Belege je Seite)
# ------------------------------
class EvidencePage(Base):
    __tablename__ = "evidence_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("search_runs.id", ondelete="CASCADE"), index=True)

    url: Mapped[str] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_score: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
'@ | Set-Content -Path "$root\src\newsapp\models.py" -Encoding UTF8

# --- scripts/init_db.py (Tabellen anlegen + Beispiel-Template) ---
@'
from newsapp.database import engine, SessionLocal
from newsapp.models import Base, Template

def main():
    # Tabellen anlegen
    Base.metadata.create_all(bind=engine)

    # Beispiel-Template (nur wenn noch nicht vorhanden)
    db = SessionLocal()
    try:
        if not db.query(Template).filter(Template.name == "Six Payments – Focused").first():
            t = Template(
                name="Six Payments – Focused",
                urls_csv="https://www.six-group.com/de/products-services/banking-services/payment-standardization/standards/qr-bill.html, https://www.six-group.com/de/products-services/banking-services/payment-standardization.html",
                keywords_csv="QR-Rechnung, ISO20022, IBAN, SEPA, EBICS",
                persona="Du bist Experte für Zahlungsverkehr/Cash Management.",
                assignment="Analysiere nur, was belegt ist. Keine Firmenbeschreibungen. Fokussiere auf QR-Rechnung, ISO20022, SEPA, IBAN, EBICS, Schnittstellen/Spec-Changes.",
                output_types=["summary","changes","action","risk","page_analysis"],
                scoring_rules={"weights":{"high":3,"med":2,"low":1},"trusted_boost":3,"allowed_boost":1,"max_passages_per_url":8}
            )
            db.add(t)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    main()
'@ | Set-Content -Path "$root\scripts\init_db.py" -Encoding UTF8

Write-Host "✅ DB-Modelle & init_db.py erstellt."
Write-Host "➡  DB initialisieren:"
Write-Host "    cd `"$root\src`""
Write-Host "    ..\ .venv\Scripts\python.exe ..\scripts\init_db.py"
