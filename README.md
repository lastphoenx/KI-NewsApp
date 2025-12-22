# NewsApp

NewsApp ist eine automatisierte News-Monitoring-Plattform für Cash-Management und Zahlungsverkehrs-Teams. Sie durchsucht konfigurierbare Quellen nach relevanten Änderungen (z.B. ISO 20022, EBICS, QR-Rechnung) und generiert KI-gestützte Analysen mit Änderungen, Actions und Risiken.

## 🏗️ Tech Stack

**Backend:**
- Python 3.10+ / FastAPI / SQLAlchemy / SQLite
- Uvicorn (ASGI Server)
- LLM-Integration (OpenAI, Anthropic, Mistral)

**Frontend:**
- **Admin UI:** Streamlit (Template- und Run-Verwaltung)
- **Dashboard:** React 19 + TypeScript + Vite
  - TanStack React Table, Recharts, Tailwind CSS

## 🚀 Installation

### 1. Repository klonen
```bash
git clone <repo-url>
cd NewsApp
```

### 2. Python-Umgebung einrichten
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# oder: source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Node.js-Umgebung einrichten (für Dashboard)
```bash
cd dashboard
npm install
cd ..
```

### 4. Umgebungsvariablen konfigurieren
```bash
# .env.example nach .env kopieren
copy .env.example .env  # Windows
# oder: cp .env.example .env  # Linux/Mac

# WICHTIG: Öffne .env und trage deine API-Keys ein!
# Mindestens einen der folgenden API-Keys benötigst du:
# - OPENAI_API_KEY=sk-...           (von https://platform.openai.com/api-keys)
# - ANTHROPIC_API_KEY=sk-ant-...    (von https://console.anthropic.com/)
# - MISTRAL_API_KEY=...             (von https://console.mistral.ai/)
```

### 5. Datenbank initialisieren
```bash
# Die Datenbank (app.db) wird automatisch beim ersten Start erstellt
# Optional: Initialisiere mit dem Migrations-Script
python scripts/init_db.py
```

### 6. Server starten

**Option A: Alle Server parallel (empfohlen)**
```bash
.\start-servers.ps1  # Windows
```

**Option B: Manuell**
```bash
# Terminal 1 - Backend (FastAPI)
uvicorn newsapp.main:app --host 0.0.0.0 --port 8008 --app-dir src --reload

# Terminal 2 - Admin UI (Streamlit)
streamlit run streamlit_app.py

# Terminal 3 - Dashboard (React)
cd dashboard
npm run dev
```

### 7. (Optional) Seed-Daten hinzufügen
```bash
# Nachdem die Server laufen (Schritt 6):
python seed-data.py
```

### 8. Öffnen
- **API Docs:** http://localhost:8008/docs
- **Admin UI:** http://localhost:8501
- **Dashboard:** http://localhost:5173

## 🔒 Sicherheit

⚠️ **WICHTIG:** Die `.env` Datei enthält sensible API-Keys und ist in `.gitignore` enthalten. Committe sie **NIEMALS** ins Repository!

## 📚 Weitere Dokumentation

- [QUICK_START.md](QUICK_START.md) - Detaillierte Feature-Übersicht und Workflow
- [README_ADMIN.md](README_ADMIN.md) - Admin-Interface Anleitung
- `scripts/maintenance/` - Utility-Scripts für Entwickler

## 🗂️ Projektstruktur

```
├── src/newsapp/          # Backend-Code (FastAPI)
│   ├── routers/          # API Endpoints
│   ├── utils/            # Fetcher, LLM, Normalizer
│   ├── models.py         # SQLAlchemy Models
│   └── main.py           # FastAPI App
├── dashboard/            # React Frontend (Vite)
├── scripts/              # Setup & Migration
│   └── maintenance/      # Dev-Utilities
├── tests/                # Tests
├── streamlit_app.py      # Admin UI
├── requirements.txt      # Python Dependencies
└── .env.example          # Environment Template
```

## 🔧 Maintenance

**Datenbank zurücksetzen:**
```bash
.\scripts\maintenance\reset-db.ps1
```

**Seed-Daten hinzufügen:**
```bash
python seed-data.py
```

## 📝 Lizenz

[Lizenz hier einfügen]

