# Start Backend (FastAPI), Admin UI (Streamlit) und Dashboard (React) parallel

$root = $PSScriptRoot

Write-Host "🚀 Starte NewsApp..." -ForegroundColor Green
Write-Host ""

# Backend in neuem Terminal starten
Write-Host "📡 Starte Backend (FastAPI)..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$root'; uvicorn newsapp.main:app --host 0.0.0.0 --port 8008 --app-dir src --reload"

# Kurz warten
Start-Sleep -Seconds 2

# Admin UI in neuem Terminal starten
Write-Host "🎨 Starte Admin UI (Streamlit)..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$root'; streamlit run streamlit_app.py"

# Kurz warten
Start-Sleep -Seconds 2

# Dashboard in neuem Terminal starten
Write-Host "📊 Starte Dashboard (React)..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$root\dashboard'; npm run dev"

Write-Host ""
Write-Host "✅ Alle Server gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "Öffne in deinem Browser:" -ForegroundColor Yellow
Write-Host "  - API Docs:   http://localhost:8008/docs" -ForegroundColor White
Write-Host "  - Admin UI:   http://localhost:8501" -ForegroundColor White
Write-Host "  - Dashboard:  http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Zum Beenden: Schließe die Server-Terminals oder drücke STRG+C" -ForegroundColor Gray
