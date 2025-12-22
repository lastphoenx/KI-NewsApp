# Datenbank neu erstellen
Write-Host "🗄️  Erstelle Datenbank neu..." -ForegroundColor Cyan

# Alte DB löschen
if (Test-Path "app.db") {
    Remove-Item "app.db" -Force
    Write-Host "✓ Alte Datenbank gelöscht" -ForegroundColor Gray
}

# Neue DB erstellen - mit Force-Reload aller Module
python -c @"
import sys
import importlib

# Sys-Path setzen
sys.path.insert(0, 'src')

# Alle newsapp-Module aus dem Cache entfernen
modules_to_remove = [key for key in sys.modules.keys() if key.startswith('newsapp')]
for mod in modules_to_remove:
    del sys.modules[mod]

# Jetzt frisch importieren
from newsapp.database import engine
from newsapp.models import Base

# DB erstellen
Base.metadata.create_all(bind=engine)

print('✓ Datenbank-Tabellen erstellt')
for t in Base.metadata.sorted_tables:
    print(f'  - {t.name}')
"@

Write-Host ""
Write-Host "✅ Fertig!" -ForegroundColor Green
