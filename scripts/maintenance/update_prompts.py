"""
Update AI instructions for consistent Change->Action->Risk mapping

This is a maintenance script used to update Output Type AI instructions via API.
Useful when refining prompts or fixing output consistency issues.

Usage:
1. Ensure the API server is running (uvicorn)
2. Run: python scripts/maintenance/update_prompts.py
3. Verify changes in Admin UI or via GET /output-types/{id}

Note: Hardcoded IDs (2=Changes, 3=Actions, 4=Risks) - adjust if schema changes.
"""
import httpx

BASE_URL = "http://localhost:8008"

# 1. Changes & Deadlines (ID: 2) - require minimum 3
changes_update = {
    "name": "Changes & Deadlines",
    "description": "Konkrete Änderungen an Standards, Spezifikationen, Formaten mit Deadlines",
    "ai_instructions": (
        "Extrahiere MINDESTENS 3 konkrete Änderungen/Anpassungen an Standards, Spezifikationen, "
        "Formaten oder Schnittstellen (z.B. ISO 20022, pain.001, camt.053, EBICS, QR-Rechnung, "
        "Instant Payments). Liefere, falls vorhanden, ein Wirksamkeitsdatum oder Deadline. "
        "Wenn weniger als 3 belegte Änderungen vorhanden sind, ergänze sinnvolle verwandte Themen aus dem Material."
    ),
    "expected_schema": {
        "type": "object",
        "properties": {
            "changes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "description": {"type": "string"},
                        "effective_date": {"type": "string"},
                        "impact": {"type": "string", "enum": ["high", "medium", "low"]},
                        "affected_interfaces": {"type": "array", "items": {"type": "string"}},
                        "spec_reference": {"type": "string"},
                        "change_type": {
                            "type": "string",
                            "enum": ["standard_update", "deprecation", "new_method", "operational", "fee"]
                        }
                    },
                    "required": ["topic", "description"]
                }
            }
        },
        "required": ["changes"]
    },
    "dashboard_rules": {
        "component": "list+badges",
        "sort_by": ["impact:desc", "effective_date:asc"],
        "badge_fields": ["impact", "change_type"]
    }
}

# 2. Actions (ID: 3) - 1:1 mapping to changes
actions_update = {
    "name": "Actions",
    "description": "Umsetzbare To-Dos für Cash-Management-Team mit Prioritäten",
    "ai_instructions": (
        "Formuliere umsetzbare To-Dos für ein Cash-Management-Team. "
        "WICHTIG: Generiere für JEDE Change aus 'changes' array genau EINE korrespondierende Action. "
        "Die Anzahl der Actions MUSS exakt der Anzahl der Changes entsprechen. "
        "Priorisiere nach Auswirkung auf den Betrieb. Gib nach Möglichkeit Deadline, "
        "Aufwand (Personentage) und kurze Begründung."
    ),
    "expected_schema": {
        "type": "object",
        "properties": {
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        "deadline": {"type": "string"},
                        "effort": {"type": "string"},
                        "owner_role": {"type": "string"},
                        "reason": {"type": "string"},
                        "dependencies": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["action", "priority"]
                }
            }
        },
        "required": ["actions"]
    },
    "dashboard_rules": {
        "component": "todo-list",
        "group_by": "priority",
        "deadline_field": "deadline"
    }
}

# 3. Risk Analysis (ID: 4) - 1:1 mapping to changes
risks_update = {
    "name": "Risk Analysis",
    "description": "Bewertung von Risiken beim Nichtstun mit Schweregrad und Mitigation",
    "ai_instructions": (
        "Bewerte Risiken beim Nichtstun (Business/Tech/Compliance/Ops). "
        "WICHTIG: Generiere für JEDE Change aus 'changes' array genau EIN korrespondierendes Risk. "
        "Die Anzahl der Risks MUSS exakt der Anzahl der Changes entsprechen. "
        "Schätze Schweregrad und Eintrittswahrscheinlichkeit, nenne Konsequenz, Mitigation und Detection."
    ),
    "expected_schema": {
        "type": "object",
        "properties": {
            "risks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "risk": {"type": "string"},
                        "area": {"type": "string", "enum": ["Business", "Tech", "Compliance", "Ops"]},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "likelihood": {"type": "string", "enum": ["high", "medium", "low"]},
                        "consequence": {"type": "string"},
                        "mitigation": {"type": "string"},
                        "detection": {"type": "string"}
                    },
                    "required": ["risk", "area", "severity", "likelihood", "mitigation"]
                }
            }
        },
        "required": ["risks"]
    },
    "dashboard_rules": {
        "component": "risk-matrix",
        "axes": ["likelihood", "severity"],
        "badge": "area"
    }
}

def update_output_type(type_id: int, data: dict):
    """Update a single output type via API"""
    url = f"{BASE_URL}/output-types/{type_id}"
    response = httpx.put(url, json=data, timeout=30.0)
    response.raise_for_status()
    print(f"✓ Updated Output Type {type_id}: {data['name']}")
    return response.json()

if __name__ == "__main__":
    print("Updating AI instructions for consistent Change->Action->Risk mapping...\n")
    
    try:
        update_output_type(2, changes_update)
        update_output_type(3, actions_update)
        update_output_type(4, risks_update)
        print("\n✓ All prompts updated successfully!")
        print("\nNext steps:")
        print("1. Create a new Run in the Streamlit admin")
        print("2. Check Dashboard - Changes, Actions, and Risks should now have equal counts")
    except Exception as e:
        print(f"✗ Error: {e}")
