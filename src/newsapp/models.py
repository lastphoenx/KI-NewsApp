from __future__ import annotations
from typing import Optional, Any
from sqlalchemy import String, Integer, Text, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy import Table, Column

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
    scoring_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)     # {"weights":{"high":3,"med":2,"low":1}, ...}

    # d) KI-Konfiguration (pro Template)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)   # openai|anthropic|mistral
    ai_model: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)      # z.B. gpt-4o-mini, claude-3-5-sonnet-latest
    ai_temperature: Mapped[Optional[float]] = mapped_column(nullable=True)          # 0.0-1.0

    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True, server_default=None)

    runs: Mapped[list["SearchRun"]] = relationship(back_populates="template", cascade="all, delete-orphan")
    output_types: Mapped[list["OutputType"]] = relationship(
        secondary="template_output_types", back_populates="templates"
    )

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
    
    run: Mapped["SearchRun"] = relationship(back_populates="pages")

# --- M:N Zuordnung Template <-> OutputType
TemplateOutputType = Table(
    "template_output_types", Base.metadata,
    Column("template_id", ForeignKey("templates.id", ondelete="CASCADE"), primary_key=True),
    Column("output_type_id", ForeignKey("output_types.id", ondelete="CASCADE"), primary_key=True),
)

class OutputType(Base):
    __tablename__ = "output_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    # vom Admin pflegbar – keine Hardcodes:
    description: Mapped[Optional[str]] = mapped_column(Text)
    ai_instructions: Mapped[Optional[str]] = mapped_column(Text)     # Prompt-Snippet
    expected_schema: Mapped[Optional[dict]] = mapped_column(JSON)    # JSON-Schema / Feldliste
    dashboard_rules: Mapped[Optional[dict]] = mapped_column(JSON)    # wie rendern (Badges, Sortierung …)

    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True, server_default=None)

    templates: Mapped[list["Template"]] = relationship(
        secondary=TemplateOutputType, back_populates="output_types"
    )
