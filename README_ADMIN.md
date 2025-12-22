# NewsApp API & Admin Interface

## Setup

1. Virtuelle Umgebung aktivieren:
```
.venv\Scripts\Activate.ps1
```

2. Dependencies installieren:
```
pip install -r requirements.txt
```

3. Datenbank neu initialisieren (bei Schema-Änderungen):
```
Remove-Item app.db -ErrorAction SilentlyContinue
python -c "from src.newsapp.main import app; from src.newsapp.database import engine; from src.newsapp.models import Base; Base.metadata.create_all(bind=engine); print('DB created')"
```

## API starten

```
uvicorn newsapp.main:app --host 0.0.0.0 --port 8008 --app-dir src --reload
```

API läuft auf: http://localhost:8008
API Docs: http://localhost:8008/docs

## Streamlit Admin Interface starten

```
streamlit run streamlit_app.py
```

Die Admin-Oberfläche läuft auf: http://localhost:8501

## Features

### 1. Output-Typen (Tab 1)
- Verwalte Output-Typen ohne Hardcodes
- Definiere AI-Anweisungen, Expected Schema und Dashboard Rules
- Komplett über UI pflegbar

### 2. Templates (Tab 2)
- Erstelle Such-Templates mit URLs und Keywords
- Ordne Output-Typen per M:N Relationship zu
- Definiere Persona und Assignment für AI

### 3. Runs & Ergebnisse (Tab 3)
- Übersicht aller Search Runs
- Detailansicht mit Summary, Changes, Actions, Risks
- Findings per Page Analyse

## API Endpoints

### Output-Types
- GET /output-types - Liste aller Output-Typen
- POST /output-types - Neuen Output-Typ erstellen
- GET /output-types/{oid} - Output-Typ Details
- PUT /output-types/{oid} - Output-Typ aktualisieren
- DELETE /output-types/{oid} - Output-Typ löschen

### Templates
- GET /templates - Liste aller Templates
- POST /templates - Neues Template erstellen (mit output_type_ids)
- GET /templates/{tid} - Template Details
- PUT /templates/{tid} - Template aktualisieren
- DELETE /templates/{tid} - Template löschen

### Runs
- GET /runs - Liste aller Runs
- POST /runs - Neuen Run starten
- GET /runs/{rid} - Run Details
- PUT /runs/{rid}/result - Ergebnisse an Run anhängen
- DELETE /runs/{rid} - Run löschen

## Datenmodell

### M:N Relationship
Templates ←→ OutputTypes über 	emplate_output_types Tabelle

### Entfernte Hardcodes
- output_types JSON-Feld im Template wurde durch M:N Relationship ersetzt
- Output-Typen sind nun vollständig pflegbar über API/UI
