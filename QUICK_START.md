# NewsApp - Quick Start Guide

## Was wurde implementiert?

### ✅ 1. Datenmodell erweitert (models.py)
- OutputType Klasse hinzugefügt
- M:N Relationship zwischen Template und OutputType
- Entfernung des hardcodierten output_types JSON-Felds

### ✅ 2. API Router erstellt
- /output-types - Vollständiger CRUD für Output-Typen
- /templates - Erweitert um output_type_ids Parameter
- /runs/{rid}/result - Endpoint zum Anhängen von Ergebnissen

### ✅ 3. Streamlit Admin Interface
- Tab 1: Output-Typen verwalten
- Tab 2: Templates erstellen mit Output-Typ-Zuordnung
- Tab 3: Runs und Ergebnisse anzeigen

## Schnellstart

### Option A: Mit Skript (empfohlen)
```powershell
# Beide Server parallel starten
.\start-servers.ps1
```

### Option B: Manuell

#### 1. Datenbank neu erstellen (bei Schema-Änderungen)
```powershell
# Einfach mit Skript
.\reset-db.ps1

# Oder manuell
Remove-Item app.db -ErrorAction SilentlyContinue
python scripts/migrate_db.py
```

#### 2. API starten (Terminal 1)
```powershell
uvicorn newsapp.main:app --host 0.0.0.0 --port 8008 --app-dir src --reload
```

#### 3. Streamlit UI starten (Terminal 2)
```powershell
streamlit run streamlit_app.py
```

#### 4. Öffnen
- API: http://localhost:8008/docs
- Admin UI: http://localhost:8501

## Workflow

1. **Output-Typen definieren** (Tab 1)
   - z.B. "Summary", "Changes", "Actions", "Risks"
   - Mit AI-Instructions und Schema

2. **Templates erstellen** (Tab 2)
   - URLs und Keywords definieren
   - Output-Typen auswählen (M:N)
   - Persona und Assignment setzen

3. **Runs ausführen** (Tab 3)
   - POST /runs mit template_id
   - PUT /runs/{rid}/result zum Anhängen von Ergebnissen
   - Ergebnisse in UI anzeigen

## Wichtige Änderungen

### Templates Router
- output_type_ids: Optional[List[int]] in TemplateIn
- Automatische M:N Zuordnung beim Create/Update

### Keine Hardcodes mehr!
- Alle Output-Typen pflegbar über UI/API
- Flexibles Schema pro Output-Typ
- AI-Instructions pro Output-Typ konfigurierbar
