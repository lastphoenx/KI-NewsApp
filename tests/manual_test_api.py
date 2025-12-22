"""Quick test to see what error occurs when creating a run"""
import requests

payload = {
    "template_id": 1,
    "ai_provider": "openai",
    "ai_model": "gpt-4o-mini",
    "use_ai": True
}

try:
    response = requests.post("http://localhost:8008/runs", json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
