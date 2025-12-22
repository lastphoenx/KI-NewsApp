"""
Seed-Skript zum Anlegen von Output-Typen und Templates via API
"""
import requests
import json
import os
from typing import Dict, Any

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8008")

def create_output_type(data: Dict[str, Any]) -> Dict:
    """Erstellt einen Output-Type via API"""
    response = requests.post(f"{API_BASE}/output-types", json=data)
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Output-Type erstellt: {result['name']} (ID: {result['id']})")
        return result
    else:
        print(f"✗ Fehler bei {data['name']}: {response.status_code} - {response.text}")
        return {}

def create_template(data: Dict[str, Any]) -> Dict:
    """Erstellt ein Template via API"""
    response = requests.post(f"{API_BASE}/templates", json=data)
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Template erstellt: {result['name']} (ID: {result['id']})")
        return result
    else:
        print(f"✗ Fehler bei {data['name']}: {response.status_code} - {response.text}")
        return {}

def main():
    print("=" * 60)
    print("SEED-DATA für NewsApp")
    print("=" * 60)
    
    # ========================================
    # OUTPUT-TYPEN
    # ========================================
    print("\n1. Erstelle Output-Typen...\n")
    
    output_types = [
        {
            "name": "Summary",
            "description": "Präzise Übersicht in 3-6 Bulletpoints mit Relevanz-Score",
            "ai_instructions": "Gib eine präzise Übersicht in 3–6 Bulletpoints. Bewerte die Relevanz für Cash-Management (0–10) und gib eine grobe Confidence (0–1). Keine Firmenbeschreibungen, nur belegte Fakten.",
            "expected_schema": {
                "type": "object",
                "properties": {
                    "relevance_score": {"type": "number", "minimum": 0, "maximum": 10},
                    "summary": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["relevance_score", "summary"]
            },
            "dashboard_rules": {
                "component": "score+bullets",
                "score_field": "relevance_score",
                "bullets_field": "summary"
            }
        },
        {
            "name": "Changes & Deadlines",
            "description": "Konkrete Änderungen an Standards, Spezifikationen, Formaten mit Deadlines",
            "ai_instructions": "Extrahiere NUR konkrete Änderungen/Anpassungen an Standards, Spezifikationen, Formaten oder Schnittstellen (z.B. ISO 20022, pain.001, camt.053, EBICS, QR-Rechnung, Instant Payments). Liefere, falls vorhanden, ein Wirksamkeitsdatum oder Deadline. Wenn keine belegten Änderungen vorhanden sind, leere Liste.",
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
                                "change_type": {"type": "string", "enum": ["standard_update", "deprecation", "new_method", "operational", "fee"]}
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
        },
        {
            "name": "Actions",
            "description": "Umsetzbare To-Dos für Cash-Management-Team mit Prioritäten",
            "ai_instructions": "Formuliere umsetzbare To-Dos für ein Cash-Management-Team. Priorisiere nach Auswirkung auf den Betrieb. Gib nach Möglichkeit Deadline, Aufwand (Personentage) und kurze Begründung.",
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
        },
        {
            "name": "Risk Analysis",
            "description": "Bewertung von Risiken beim Nichtstun mit Schweregrad und Mitigation",
            "ai_instructions": "Bewerte Risiken beim Nichtstun (Business/Tech/Compliance/Ops). Schätze Schweregrad und Eintrittswahrscheinlichkeit, nenne Konsequenz und Mitigation.",
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
        },
        {
            "name": "Page Analysis",
            "description": "Pro Seite: Relevanz-Score, Key Findings, Deadlines, Spec-Refs",
            "ai_instructions": "Für jede Seite: Relevanz 0–10, 1–3 Key Findings (belegte Zitate/Paraphrasen), erkannte Deadlines und ggf. Referenzen auf Spezifikationen.",
            "expected_schema": {
                "type": "object",
                "properties": {
                    "findings_per_page": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"},
                                "page_relevance": {"type": "number", "minimum": 0, "maximum": 10},
                                "key_findings": {"type": "array", "items": {"type": "string"}},
                                "deadlines": {"type": "array", "items": {"type": "string"}},
                                "spec_refs": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["url", "page_relevance", "key_findings"]
                        }
                    }
                },
                "required": ["findings_per_page"]
            },
            "dashboard_rules": {
                "component": "accordion-by-score",
                "score_field": "page_relevance"
            }
        },
        {
            "name": "Timeline",
            "description": "Chronologische Liste von Deadlines, Effective Dates, Milestones",
            "ai_instructions": "Baue eine chronologische Liste (Deadlines, Effective Dates, Milestones) aus dem Material.",
            "expected_schema": {
                "type": "object",
                "properties": {
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string"},
                                "event": {"type": "string"},
                                "type": {"type": "string", "enum": ["deadline", "effective", "milestone"]},
                                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                "related_topics": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["date", "event", "type"]
                        }
                    }
                },
                "required": ["timeline"]
            },
            "dashboard_rules": {
                "component": "timeline",
                "sort_by": ["date:asc"]
            }
        }
    ]
    
    created_output_types = []
    for ot in output_types:
        result = create_output_type(ot)
        if result:
            created_output_types.append(result)
    
    # ========================================
    # TEMPLATE
    # ========================================
    print("\n2. Erstelle Template...\n")
    
    # Hole alle Output-Type IDs für die Verknüpfung
    output_type_ids = [ot['id'] for ot in created_output_types]
    
    template = {
        "name": "SIX – Payments Standards & Interfaces",
        "urls_csv": "https://www.six-group.com/de/products-services/banking-services/payment-standardization.html,https://www.six-group.com/de/products-services/banking-services/payment-standardization/standards/qr-bill.html,https://www.six-group.com/en/products-services/banking-services/billing-and-payments/instant-payments.html,https://www.six-group.com/en/products-services/banking-services/interbank-clearing.html",
        "keywords_csv": "QR-Rechnung, QR Rechnung, QR-bill, ISO20022, pain.001, pain.002, camt.052, camt.053, camt.054, instant payment, SCT Inst, SEPA, IBAN, EBICS, API, Schnittstelle, Spezifikation, Schema, XSD, Validierung, Referenz",
        "persona": "Ich bin Leiter Cash Management eines großen Unternehmens. Ich brauche ausschließlich belegte Informationen, die Auswirkungen auf Zahlungsprozesse, Formate und Schnittstellen haben (Einführung neuer Zahlarten, Format-/Schema-Änderungen, Versionen, Migrationsfristen, Abkündigungen, Validierungsregeln).",
        "assignment": "Analysiere nur nachprüfbare Inhalte. Fokus: QR-Rechnung, ISO 20022 (pain/camt), SEPA/SCT Inst, IBAN, EBICS, banknahe APIs. Erkenne Änderungen, Deadlines, betroffene Schnittstellen/Message-Types, Risiken beim Nichtstun und konkrete Handlungsempfehlungen. Nenne Spezifikationsreferenzen und Wirksamkeitsdaten. Keine allgemeinen Firmenbeschreibungen.",
        "trusted_urls": ["six-group.com"],
        "allowed_domains": ["epc-cep.eu", "iso20022.org", "ecb.europa.eu", "swisspayments.ch", "paymentstandards.ch"],
        "keyword_aliases": {
            "QR-Rechnung": ["QR Rechnung", "QR-bill", "QR bill"],
            "instant payment": ["instant payments", "SCT Inst", "real-time payments"],
            "camt.053": ["camt 053", "CAMT053"],
            "camt.054": ["camt 054", "CAMT054"],
            "pain.001": ["pain 001", "PAIN001"],
            "EBICS": ["ebics", "ebics 3.0", "ebics3"]
        },
        "scoring_rules": {
            "weights": {"high": 3, "medium": 2, "low": 1},
            "trusted_boost": 3,
            "allowed_boost": 1,
            "max_passages_per_url": 8,
            "keyword_impact": {
                "QR-Rechnung": 3,
                "instant payment": 3,
                "ISO20022": 3,
                "pain.001": 2,
                "camt.053": 2,
                "SEPA": 2,
                "EBICS": 2
            }
        },
        "output_type_ids": output_type_ids
    }
    
    created_template = create_template(template)
    
    # ========================================
    # ZUSAMMENFASSUNG
    # ========================================
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"✓ {len(created_output_types)} Output-Typen erstellt")
    print(f"✓ 1 Template erstellt (mit {len(output_type_ids)} Output-Typen verknüpft)")
    print("\nÖffne die Admin-UI: http://localhost:8501")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ FEHLER: API nicht erreichbar!")
        print("Starte zuerst die Server mit: .\\start-servers.ps1")
    except Exception as e:
        print(f"\n✗ FEHLER: {e}")
        import traceback
        traceback.print_exc()
