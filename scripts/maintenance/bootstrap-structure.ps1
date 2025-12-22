# bootstrap-structure.ps1
$root = $PSScriptRoot
$folders = @(
  "$root\.vscode",
  "$root\src\newsapp\routers",
  "$root\src\newsapp\utils",
  "$root\src\newsapp",
  "$root\scripts",
  "$root\tests"
)

foreach ($f in $folders) {
  New-Item -ItemType Directory -Force -Path $f | Out-Null
}

# --- VS Code settings/launch ---
@'
{
  "python.defaultInterpreterPath": ".venv\\Scripts\\python.exe",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true
}
'@ | Set-Content -Path "$root\.vscode\settings.json" -Encoding UTF8

@'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run API (uvicorn)",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["newsapp.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "cwd": "${workspaceFolder}\src"
    }
  ]
}
'@ | Set-Content -Path "$root\.vscode\launch.json" -Encoding UTF8

# --- project files ---
@'
fastapi
uvicorn[standard]
pydantic>=2
SQLAlchemy>=2
python-dotenv
charset-normalizer
'@ | Set-Content -Path "$root\requirements.txt" -Encoding UTF8

@'
[project]
name = "newsapp"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []
'@ | Set-Content -Path "$root\pyproject.toml" -Encoding UTF8

@'
# NewsApp

## Quickstart
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn newsapp.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src

'@ | Set-Content -Path "$root\README.md" -Encoding UTF8

@'
DB_URL=sqlite:///app.db
'@ | Set-Content -Path "$root\.env" -Encoding UTF8

# --- package skeleton ---
@'
from .database import Base
from .models import Template, SearchRun, EvidencePage
'@ | Set-Content -Path "$root\src\newsapp\__init__.py" -Encoding UTF8

@'
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()
DB_URL = os.getenv("DB_URL", "sqlite:///app.db")

class Base(DeclarativeBase):
    pass

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    from contextlib import contextmanager
    @contextmanager
    def _session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    return _session()
'@ | Set-Content -Path "$root\src\newsapp\database.py" -Encoding UTF8

@'
from fastapi import FastAPI
from .database import engine
from .models import Base

app = FastAPI(title="NewsApp API")

@app.get("/health")
def health():
    return {"status": "ok"}

# Tables are created by the DB bootstrap, but this keeps dev tidy
Base.metadata.create_all(bind=engine)
'@ | Set-Content -Path "$root\src\newsapp\main.py" -Encoding UTF8

# empty placeholders for later
"" | Set-Content -Path "$root\src\newsapp\routers\templates.py" -Encoding UTF8
"" | Set-Content -Path "$root\src\newsapp\routers\runs.py" -Encoding UTF8
"" | Set-Content -Path "$root\src\newsapp\utils\normalizer.py" -Encoding UTF8
"" | Set-Content -Path "$root\tests\test_smoke.py" -Encoding UTF8

Write-Host "✅ Struktur erstellt unter $root"