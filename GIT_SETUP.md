# Git Setup Instructions

## Vor dem ersten Commit

Stelle sicher, dass alle sensiblen Daten geschützt sind:

### 1. Git initialisieren
```bash
git init
```

### 2. .env aus Git ausschließen (falls vorhanden)
Die `.env` Datei sollte **NIEMALS** ins Repository. Sie wird bereits durch `.gitignore` ausgeschlossen, aber zur Sicherheit:

```bash
# Prüfe ob .env tracked würde
git status

# Falls .env in der Liste erscheint, entferne sie:
git rm --cached .env

# Stelle sicher dass .env.example NICHT ignoriert wird
git add .env.example
```

### 3. Status prüfen
```bash
git status
```

Diese Dateien sollten **NICHT** in der Liste sein:
- ❌ `.env` (nur `.env.example` sollte dabei sein)
- ❌ `app.db`
- ❌ `.venv/`
- ❌ `__pycache__/`
- ❌ `node_modules/`

### 4. Erster Commit
```bash
git add .
git commit -m "Initial commit - NewsApp"
```

### 5. Remote hinzufügen und pushen
```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## Nach dem Klonen (für neue Entwickler)

1. Repository klonen
2. `.env.example` nach `.env` kopieren
3. API-Keys in `.env` eintragen
4. Installation gemäß [README.md](README.md) durchführen

## Wichtig

Die `.env` Datei enthält sensible API-Keys und darf **NIEMALS** ins Repository committed werden!
