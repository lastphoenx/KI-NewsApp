"""
Datenbank neu erstellen mit neuen Schema-Änderungen
- Entfernt output_types JSON-Feld aus Template
- Fügt OutputType Tabelle hinzu
- Erstellt M:N Relationship template_output_types
"""
import os
import sys

# Füge src/ zum Python-Pfad hinzu (eine Ebene über scripts/)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from newsapp.database import engine
from newsapp.models import Base

if __name__ == "__main__":
    print("Erstelle Datenbank-Tabellen...")
    Base.metadata.create_all(bind=engine)
    print("✓ Fertig!")
    print("\nFolgende Tabellen wurden erstellt:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
