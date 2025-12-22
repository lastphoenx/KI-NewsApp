"""
Zentrale Konfiguration für LLM-Provider und Modelle
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env laden (falls vorhanden)
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

def get_api_keys():
    """Gibt Dictionary mit allen API-Keys zurück"""
    return {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "mistral": os.getenv("MISTRAL_API_KEY"),
    }

# Default-Werte aus .env oder Fallbacks
DEFAULTS = {
    "provider": os.getenv("DEFAULT_AI_PROVIDER", "openai"),
    "model": os.getenv("DEFAULT_AI_MODEL", "gpt-4o-mini"),
    "temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.0")),
}

# Empfohlene Modelle pro Provider
RECOMMENDED_MODELS = {
    "openai": {
        "fast": "gpt-4o-mini",
        "quality": "gpt-4o",
    },
    "anthropic": {
        # Verwende bevorzugt aktuelle Claude-3.5 – die "latest"-Alias meidet veraltete Varianten
        "fast": "claude-3-5-haiku-latest",
        "quality": "claude-3-5-sonnet-latest",
    },
    "mistral": {
        "fast": "mistral-small-latest",
        "quality": "mistral-large-latest",
    },
}
