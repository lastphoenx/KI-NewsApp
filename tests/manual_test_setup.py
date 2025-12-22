"""Quick test for run creation"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, 'src')

from newsapp.database import SessionLocal
from newsapp.models import Template
from newsapp.config import get_api_keys, DEFAULTS

db = SessionLocal()
t = db.query(Template).get(1)

if t:
    print(f"[OK] Template gefunden: {t.name}")
    print(f"  URLs: {len(t.urls_list())} Stueck")
    print(f"  Keywords: {len(t.keywords_list())} Stueck")
    print(f"  Output-Types: {len(t.output_types)} Stueck")
else:
    print("[ERROR] Template ID 1 nicht gefunden!")
    sys.exit(1)

# API-Keys testen
keys = get_api_keys()
print(f"\n[OK] API-Keys:")
print(f"  OpenAI: {'JA' if keys.get('openai') and len(keys['openai']) > 10 else 'NEIN'}")
print(f"  Anthropic: {'JA' if keys.get('anthropic') and len(keys.get('anthropic', '')) > 10 else 'NEIN'}")
print(f"  Mistral: {'JA' if keys.get('mistral') and len(keys.get('mistral', '')) > 10 else 'NEIN'}")

print(f"\n[OK] DEFAULTS: {DEFAULTS}")

# Teste LLM-Import
try:
    from newsapp.utils.llm_stage import run_llm_on_passages, LLMError
    print(f"\n[OK] llm_stage importierbar")
except Exception as e:
    print(f"\n[ERROR] llm_stage Import-Fehler: {e}")
    import traceback
    traceback.print_exc()
