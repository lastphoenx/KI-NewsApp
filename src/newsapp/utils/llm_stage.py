"""
Einheitlicher LLM-Aufrufer für OpenAI, Anthropic und Mistral
"""
from __future__ import annotations
import json
import httpx
import re
from typing import Optional, Dict, Any, List
from ..config import get_api_keys, DEFAULTS


class LLMError(RuntimeError):
    """Fehler bei LLM-Aufruf"""
    pass


def _clamp(s: str, max_chars=12000) -> str:
    """Kürzt Text auf max_chars Zeichen"""
    return s[:max_chars]


def _merge_expected_schema(schemas: List[dict]) -> dict:
    """
    Union der Top-Level-Felder; tolerant, um ein gemeinsames Objekt zu erzeugen.
    """
    out = {"type": "object", "properties": {}, "additionalProperties": True}
    req = set()
    
    for sch in schemas or []:
        if not isinstance(sch, dict):
            continue
        props = sch.get("properties", {})
        out["properties"].update(props)
        for r in sch.get("required", []):
            req.add(r)
    
    if req:
        out["required"] = sorted(req)
    
    return out


def _prompt_from_types(
    persona: str | None,
    assignment: str | None,
    ai_snippets: List[str],
    merged_schema: dict,
    content: str
) -> str:
    """
    Erstellt den User-Prompt aus Template-Daten und Output-Type-Anweisungen
    """
    header = []
    if persona:
        header.append(persona.strip())
    if assignment:
        header.append(assignment.strip())
    header.append("Antworte AUSSCHLIESSLICH als gültiges JSON-Objekt gemäß Schema.")
    
    body = "\n\n".join(ai_snippets)
    schema_txt = json.dumps(merged_schema, ensure_ascii=False, indent=2)
    
    return (
        "\n".join(header) + "\n\n"
        "## Aufgaben:\n" + body + "\n\n"
        "## Erwartetes JSON-Schema (vereinigt über Output-Typen):\n" + schema_txt + "\n\n"
        "## Material (konkise Auszüge):\n" + _clamp(content)
    )


async def call_llm_async(
    provider: str,
    model: str,
    system: str | None,
    user: str,
    temperature: float = 0.0,
    response_format_json: bool = True,
    timeout_s: float = 180.0
) -> dict:
    """
    Einheitlicher asynchroner LLM-Call für OpenAI, Anthropic, Mistral
    
    Returns:
        dict: Geparste JSON-Antwort
    
    Raises:
        LLMError: Bei API-Fehlern oder ungültigem JSON
    """
    keys = get_api_keys()
    
    if provider not in ("openai", "anthropic", "mistral"):
        raise LLMError(f"Unbekannter Provider: {provider}")
    
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        if provider == "openai":
            # OpenAI Chat Completions API
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {keys['openai']}"}
            messages = [
                {"role": "system", "content": system or ""},
                {"role": "user", "content": user}
            ]
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if response_format_json:
                data["response_format"] = {"type": "json_object"}
            
            r = await client.post(url, headers=headers, json=data)
            if r.status_code >= 400:
                raise LLMError(f"OpenAI API Error {r.status_code}: {r.text}")
            content = r.json()["choices"][0]["message"]["content"]

        elif provider == "anthropic":
            # Anthropic Claude Messages API
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": keys["anthropic"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            data = {
                "model": model,  # z.B. "claude-3-5-sonnet-latest"
                "max_tokens": 4000,
                "temperature": temperature,
                "system": system or "",
                "messages": [{"role": "user", "content": user}],
            }
            
            r = await client.post(url, headers=headers, json=data)
            if r.status_code >= 400:
                raise LLMError(f"Anthropic API Error {r.status_code}: {r.text}")
            msg = r.json()
            content = "".join(
                part.get("text", "")
                for part in msg.get("content", [])
                if part.get("type") == "text"
            )

        else:  # mistral
            # Mistral Chat Completions API
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {keys['mistral']}"}
            data = {
                "model": model,  # z.B. "mistral-large-latest"
                "messages": [
                    {"role": "system", "content": system or ""},
                    {"role": "user", "content": user}
                ],
                "temperature": temperature,
            }
            
            r = await client.post(url, headers=headers, json=data)
            if r.status_code >= 400:
                raise LLMError(f"Mistral API Error {r.status_code}: {r.text}")
            content = r.json()["choices"][0]["message"]["content"]

    # JSON robust parsen
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"=== LLM RAW RESPONSE === Provider: {provider}, Model: {model}")
    logger.info(f"Content length: {len(content)}")
    logger.info(f"Content preview: {content[:500]}")
    
    try:
        parsed = json.loads(content)
        logger.info(f"Successfully parsed JSON with keys: {parsed.keys() if isinstance(parsed, dict) else 'NOT A DICT'}")
        return parsed
    except Exception:
        # Minimal-Heuristik: JSON-Block herauslösen
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            try:
                parsed = json.loads(m.group(0))
                logger.info(f"Extracted JSON block with keys: {parsed.keys() if isinstance(parsed, dict) else 'NOT A DICT'}")
                return parsed
            except Exception:
                pass
        logger.error(f"Failed to parse JSON from: {content[:200]}")
        raise LLMError(f"LLM returned non-JSON response: {content[:200]}...")


async def run_llm_on_passages(
    provider: str,
    model: str,
    persona: str | None,
    assignment: str | None,
    output_types: List[dict],
    passages_text: str,
    temperature: Optional[float] = None
) -> dict:
    """
    Führt LLM-Analyse auf Text-Passagen aus
    
    Args:
        provider: openai|anthropic|mistral
        model: Modell-ID (z.B. gpt-4o-mini, claude-3-5-sonnet-latest)
        persona: Template-Persona (z.B. "Du bist Cash Management Experte")
        assignment: Template-Auftrag
        output_types: Liste von Output-Type Dicts mit ai_instructions, expected_schema
        passages_text: Zu analysierender Text
        temperature: Optional override, sonst DEFAULTS
    
    Returns:
        dict: Strukturierte LLM-Antwort (merged über alle Output-Types)
    """
    ai_snippets = [ot.get("ai_instructions") or "" for ot in output_types]
    schemas = [ot.get("expected_schema") or {} for ot in output_types]
    merged_schema = _merge_expected_schema(schemas)

    system = "Du bist ein präziser Zahlungsverkehr-Analyst. Antworte ausschließlich in validem JSON."
    user = _prompt_from_types(persona, assignment, ai_snippets, merged_schema, passages_text)
    
    result = await call_llm_async(
        provider=provider,
        model=model,
        system=system,
        user=user,
        temperature=(DEFAULTS["temperature"] if temperature is None else temperature),
        response_format_json=True,
    )
    
    return result
