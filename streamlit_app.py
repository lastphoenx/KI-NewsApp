import streamlit as st
import requests
import pandas as pd
import json

API = "http://127.0.0.1:8008"

st.set_page_config(page_title="NewsApp Admin", layout="wide")
tabs = st.tabs(["🔧 Output-Typen", "🧩 Templates", "📊 Ergebnisse"])

# ========================================
# 1) Output-Typen-Admin
# ========================================
with tabs[0]:
    st.header("Output-Typen verwalten (kein Hardcode)")
    
    # Session State initialisieren
    if "types" not in st.session_state:
        st.session_state.types = []
        # Automatisch beim ersten Laden die Daten holen
        try:
            response = requests.get(f"{API}/output-types", timeout=2)
            if response.status_code == 200:
                st.session_state.types = response.json()
        except:
            pass  # Ignorieren wenn API nicht erreichbar
    
    if "show_type_form" not in st.session_state:
        st.session_state.show_type_form = False
    if "selected_type_row" not in st.session_state:
        st.session_state.selected_type_row = None
    if "edit_type_mode" not in st.session_state:
        st.session_state.edit_type_mode = False

    if st.button("↻ Neu laden", key="load_types"):
        try:
            response = requests.get(f"{API}/output-types")
            if response.status_code == 200:
                st.session_state.types = response.json()
                st.success(f"✓ {len(st.session_state.types)} Output-Typen geladen")
            else:
                st.error(f"API Fehler {response.status_code}: {response.text[:200]}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"❌ Verbindung fehlgeschlagen: API läuft nicht auf {API}")
            st.info("Starte die API mit: .\\start-servers.ps1")
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")
    
    # === TABELLE ZUERST (oberhalb des Formulars) ===
    st.subheader("Vorhandene Output-Typen")
    
    if st.session_state.types and len(st.session_state.types) > 0:
        df = pd.DataFrame(st.session_state.types)
        
        # Spalten-Reihenfolge: id, name, description
        cols_to_show = ['id', 'name', 'description']
        available_cols = [c for c in cols_to_show if c in df.columns]
        df_display = df[available_cols] if available_cols else df
        
        # Tabelle mit Single-Row-Selection
        event = st.dataframe(
            df_display,
            on_select="rerun",
            selection_mode="single-row",
            width="stretch",
            hide_index=True,
            key="types_table"
        )
        
        # Event-Handler für Zeilen-Auswahl (mit Loop-Schutz!)
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            if st.session_state.selected_type_row != selected_idx:
                st.session_state.selected_type_row = selected_idx
                st.session_state.show_type_form = True
                st.session_state.edit_type_mode = False
    else:
        st.info("Noch keine Output-Typen vorhanden. Lade sie mit dem Button oben oder erstelle neue.")
    
    # === FORMULAR: NEU ANLEGEN (klappbar) ===
    with st.expander("➕ Neuen Output-Typ anlegen"):
        name = st.text_input("Name", key="type_name")
        desc = st.text_area("Beschreibung (optional)", key="type_desc")
        ai = st.text_area("AI-Anweisungen / Prompt-Snippet (optional)", key="type_ai")
        schema = st.text_area("Expected Schema - JSON (optional)", key="type_schema", 
                             help='z.B. {"items": [{"field": "string"}]}')
        rules = st.text_area("Dashboard Rules - JSON (optional)", key="type_rules",
                            help='z.B. {"display": "table", "sort_by": "date"}')
        
        if st.button("Speichern", type="primary", key="save_new_type"):
            if not name or not name.strip():
                st.error("Name ist ein Pflichtfeld!")
            else:
                payload = {
                    "name": name.strip(), 
                    "description": desc.strip() if desc.strip() else None,
                    "ai_instructions": ai.strip() if ai.strip() else None,
                    "expected_schema": None,
                    "dashboard_rules": None
                }
                
                # Parse Schema JSON nur wenn nicht leer
                if schema and schema.strip():
                    try: 
                        payload["expected_schema"] = json.loads(schema.strip())
                    except json.JSONDecodeError as e: 
                        st.error(f"Schema ist kein gültiges JSON: {e}")
                        st.stop()
                
                # Parse Rules JSON nur wenn nicht leer
                if rules and rules.strip():
                    try: 
                        payload["dashboard_rules"] = json.loads(rules.strip())
                    except json.JSONDecodeError as e: 
                        st.error(f"Dashboard Rules sind kein gültiges JSON: {e}")
                        st.stop()
            
                try:
                    r = requests.post(f"{API}/output-types", json=payload)
                    if r.status_code == 201:
                        st.success(f"✓ Output-Typ erstellt: {payload['name']}")
                        # Automatisch neu laden
                        st.session_state.types = requests.get(f"{API}/output-types").json()
                        st.rerun()
                    else:
                        st.error(f"Fehler {r.status_code}: {r.text}")
                except requests.exceptions.ConnectionError:
                    st.error(f"❌ Verbindung zur API fehlgeschlagen!")
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
    
    # === DETAILS-FORMULAR für ausgewählte Zeile ===
    if st.session_state.show_type_form and st.session_state.selected_type_row is not None:
        row_data = st.session_state.types[st.session_state.selected_type_row]
        
        st.markdown("---")
        
        # Header mit Edit/View Toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.session_state.edit_type_mode:
                st.subheader(f"✏️ Bearbeiten: {row_data['name']}")
            else:
                st.subheader(f"👁️ Details: {row_data['name']}")
        
        with col2:
            if st.button("✏️ Bearbeiten" if not st.session_state.edit_type_mode else "👁️ Ansicht", 
                        key="toggle_edit_type"):
                st.session_state.edit_type_mode = not st.session_state.edit_type_mode
        
        # Formular-Felder
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.edit_type_mode:
                new_name = st.text_input("Name", value=row_data['name'], key="edit_type_name")
                new_desc = st.text_area("Beschreibung", value=row_data.get('description', '') or '', key="edit_type_desc")
            else:
                st.text_input("Name", value=row_data['name'], disabled=True)
                st.text_area("Beschreibung", value=row_data.get('description', '') or '', disabled=True, height=100)
        
        with col2:
            if st.session_state.edit_type_mode:
                new_ai = st.text_area("AI-Anweisungen", value=row_data.get('ai_instructions', '') or '', key="edit_type_ai", height=100)
            else:
                st.text_area("AI-Anweisungen", value=row_data.get('ai_instructions', '') or '', disabled=True, height=100)
        
        # JSON Felder
        col1, col2 = st.columns(2)
        
        with col1:
            schema_str = json.dumps(row_data.get('expected_schema'), indent=2) if row_data.get('expected_schema') else ''
            if st.session_state.edit_type_mode:
                new_schema = st.text_area("Expected Schema (JSON)", value=schema_str, key="edit_type_schema", height=150)
            else:
                st.text_area("Expected Schema (JSON)", value=schema_str, disabled=True, height=150)
        
        with col2:
            rules_str = json.dumps(row_data.get('dashboard_rules'), indent=2) if row_data.get('dashboard_rules') else ''
            if st.session_state.edit_type_mode:
                new_rules = st.text_area("Dashboard Rules (JSON)", value=rules_str, key="edit_type_rules", height=150)
            else:
                st.text_area("Dashboard Rules (JSON)", value=rules_str, disabled=True, height=150)
        
        # Action Buttons
        if st.session_state.edit_type_mode:
            col_save, col_cancel, col_delete = st.columns([1, 1, 1])
            
            with col_save:
                if st.button("💾 Speichern", type="primary", key="save_type_changes"):
                    # Validierung und Payload erstellen
                    payload = {
                        "name": new_name.strip(),
                        "description": new_desc.strip() if new_desc.strip() else None,
                        "ai_instructions": new_ai.strip() if new_ai.strip() else None,
                        "expected_schema": None,
                        "dashboard_rules": None
                    }
                    
                    # Parse JSONs
                    try:
                        if new_schema.strip():
                            payload["expected_schema"] = json.loads(new_schema.strip())
                        if new_rules.strip():
                            payload["dashboard_rules"] = json.loads(new_rules.strip())
                    except json.JSONDecodeError as e:
                        st.error(f"JSON Fehler: {e}")
                        st.stop()
                    
                    # PUT Request
                    try:
                        r = requests.put(f"{API}/output-types/{row_data['id']}", json=payload)
                        if r.status_code == 200:
                            st.success("✅ Änderungen gespeichert!")
                            # Neu laden
                            st.session_state.types = requests.get(f"{API}/output-types").json()
                            st.session_state.edit_type_mode = False
                            st.rerun()
                        else:
                            st.error(f"Fehler {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Fehler beim Speichern: {e}")
            
            with col_cancel:
                if st.button("❌ Abbrechen", key="cancel_type_edit"):
                    st.session_state.edit_type_mode = False
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️ Löschen", key="delete_type", type="secondary"):
                    try:
                        r = requests.delete(f"{API}/output-types/{row_data['id']}")
                        if r.status_code == 200:
                            st.success(f"✅ '{row_data['name']}' gelöscht!")
                            # Neu laden und UI zurücksetzen
                            st.session_state.types = requests.get(f"{API}/output-types").json()
                            st.session_state.show_type_form = False
                            st.session_state.selected_type_row = None
                            st.session_state.edit_type_mode = False
                            st.rerun()
                        else:
                            st.error(f"Fehler {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Fehler beim Löschen: {e}")
        else:
            if st.button("❌ Schließen", key="close_type_form"):
                if st.button("❌ Schließen", key="close_type_form"):
                    st.session_state.show_type_form = False
                    st.session_state.selected_type_row = None
                    st.rerun()
    else:
        st.info("Noch keine Output-Typen vorhanden. Erstelle welche über das Formular oben.")

# ========================================
# 2) Templates
# ========================================
with tabs[1]:
    st.header("Templates (Formulare, keine Hardcodes)")
    
    # Session State initialisieren
    if "templates" not in st.session_state:
        st.session_state.templates = []
        # Automatisch beim ersten Laden
        try:
            response = requests.get(f"{API}/templates", timeout=2)
            if response.status_code == 200:
                st.session_state.templates = response.json()
        except:
            pass
    
    if "output_types_for_templates" not in st.session_state:
        st.session_state.output_types_for_templates = []
        try:
            response = requests.get(f"{API}/output-types", timeout=2)
            if response.status_code == 200:
                st.session_state.output_types_for_templates = response.json()
        except:
            pass
    
    if "show_template_form" not in st.session_state:
        st.session_state.show_template_form = False
    if "selected_template_row" not in st.session_state:
        st.session_state.selected_template_row = None
    if "edit_template_mode" not in st.session_state:
        st.session_state.edit_template_mode = False
    
    if st.button("↻ Neu laden", key="load_templates"):
        try:
            tpl_resp = requests.get(f"{API}/templates")
            typ_resp = requests.get(f"{API}/output-types")
            
            if tpl_resp.status_code == 200:
                st.session_state.templates = tpl_resp.json()
                st.success(f"✓ {len(st.session_state.templates)} Templates geladen")
            
            if typ_resp.status_code == 200:
                st.session_state.output_types_for_templates = typ_resp.json()
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Verbindung zur API fehlgeschlagen!")
            st.info("Starte die API mit: .\\start-servers.ps1")
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")
    
    # === TABELLE ZUERST ===
    st.subheader("Vorhandene Templates")
    
    if st.session_state.templates and len(st.session_state.templates) > 0:
        df = pd.DataFrame(st.session_state.templates)
        
        # Spalten: id, name, keywords_csv
        cols_to_show = ['id', 'name', 'keywords_csv']
        available_cols = [c for c in cols_to_show if c in df.columns]
        df_display = df[available_cols] if available_cols else df
        
        event = st.dataframe(
            df_display,
            on_select="rerun",
            selection_mode="single-row",
            width="stretch",
            hide_index=True,
            key="templates_table"
        )
        
        # Event-Handler für Zeilen-Auswahl (mit Loop-Schutz!)
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            if st.session_state.selected_template_row != selected_idx:
                st.session_state.selected_template_row = selected_idx
                st.session_state.show_template_form = True
                st.session_state.edit_template_mode = False
    else:
        st.info("Noch keine Templates vorhanden. Lade sie mit dem Button oben oder erstelle neue.")
    
    # === FORMULAR: NEU ANLEGEN (klappbar) ===
    with st.expander("➕ Neues Template anlegen"):
        t_name = st.text_input("Name", key="new_template_name")
        urls = st.text_area("URLs (komma-getrennt)", key="new_template_urls")
        kws = st.text_input("Stichworte (komma-getrennt)", key="new_template_kws")
        persona = st.text_area("Persona / Funktionsbeschreibung", key="new_template_persona")
        assignment = st.text_area("Auftrag", key="new_template_assignment")
        
        # Output-Typen Auswahl
        if st.session_state.output_types_for_templates:
            sel_ids = st.multiselect(
                "Output-Typen", 
                options=[t["id"] for t in st.session_state.output_types_for_templates],
                format_func=lambda i: next((x["name"] for x in st.session_state.output_types_for_templates if x["id"]==i), str(i)),
                key="new_template_output_types"
            )
        else:
            st.warning("⚠️ Keine Output-Typen verfügbar. Erstelle welche im Output-Typen Tab.")
            sel_ids = []
        
        if st.button("Speichern", type="primary", key="save_new_template"):
            if not t_name or not t_name.strip():
                st.error("Name ist ein Pflichtfeld!")
            else:
                try:
                    r = requests.post(f"{API}/templates", json={
                        "name": t_name.strip(),
                        "urls_csv": urls.strip() if urls.strip() else None,
                        "keywords_csv": kws.strip() if kws.strip() else None,
                        "persona": persona.strip() if persona.strip() else None,
                        "assignment": assignment.strip() if assignment.strip() else None,
                        "output_type_ids": sel_ids
                    })
                    if r.status_code == 201:
                        st.success(f"✓ Template erstellt: {t_name}")
                        st.session_state.templates = requests.get(f"{API}/templates").json()
                        st.rerun()
                    else:
                        st.error(f"Fehler {r.status_code}: {r.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Verbindung zur API fehlgeschlagen!")
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
    
    # === DETAILS-FORMULAR für ausgewählte Zeile ===
    if st.session_state.show_template_form and st.session_state.selected_template_row is not None:
        row_data = st.session_state.templates[st.session_state.selected_template_row]
        
        st.markdown("---")
        
        # Header mit Edit/View Toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.session_state.edit_template_mode:
                st.subheader(f"✏️ Bearbeiten: {row_data['name']}")
            else:
                st.subheader(f"👁️ Details: {row_data['name']}")
        
        with col2:
            if st.button("✏️ Bearbeiten" if not st.session_state.edit_template_mode else "👁️ Ansicht", 
                        key="toggle_edit_template"):
                st.session_state.edit_template_mode = not st.session_state.edit_template_mode
        
        # Formular-Felder
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.edit_template_mode:
                new_name = st.text_input("Name", value=row_data['name'], key="edit_template_name")
                new_urls = st.text_area("URLs (komma-getrennt)", value=row_data.get('urls_csv', '') or '', key="edit_template_urls")
                new_kws = st.text_area("Stichworte (komma-getrennt)", value=row_data.get('keywords_csv', '') or '', key="edit_template_kws")
            else:
                st.text_input("Name", value=row_data['name'], disabled=True)
                st.text_area("URLs", value=row_data.get('urls_csv', '') or '', disabled=True, height=100)
                st.text_area("Stichworte", value=row_data.get('keywords_csv', '') or '', disabled=True, height=100)
        
        with col2:
            if st.session_state.edit_template_mode:
                new_persona = st.text_area("Persona", value=row_data.get('persona', '') or '', key="edit_template_persona", height=100)
                new_assignment = st.text_area("Auftrag", value=row_data.get('assignment', '') or '', key="edit_template_assignment", height=100)
            else:
                st.text_area("Persona", value=row_data.get('persona', '') or '', disabled=True, height=100)
                st.text_area("Auftrag", value=row_data.get('assignment', '') or '', disabled=True, height=100)
        
        # Output-Typen Auswahl (nur im Edit-Mode)
        if st.session_state.edit_template_mode and st.session_state.output_types_for_templates:
            current_ids = row_data.get('output_type_ids', []) or []
            new_output_ids = st.multiselect(
                "Output-Typen",
                options=[t["id"] for t in st.session_state.output_types_for_templates],
                default=current_ids,
                format_func=lambda i: next((x["name"] for x in st.session_state.output_types_for_templates if x["id"]==i), str(i)),
                key="edit_template_output_types"
            )
        elif row_data.get('output_type_ids'):
            # Nur Anzeige
            assigned_names = [
                next((x["name"] for x in st.session_state.output_types_for_templates if x["id"]==tid), f"ID:{tid}")
                for tid in (row_data.get('output_type_ids', []) or [])
            ]
            st.text_input("Output-Typen", value=", ".join(assigned_names) if assigned_names else "Keine", disabled=True)
        
        # Action Buttons
        if st.session_state.edit_template_mode:
            col_save, col_cancel, col_delete = st.columns([1, 1, 1])
            
            with col_save:
                if st.button("💾 Speichern", type="primary", key="save_template_changes"):
                    payload = {
                        "name": new_name.strip(),
                        "urls_csv": new_urls.strip() if new_urls.strip() else None,
                        "keywords_csv": new_kws.strip() if new_kws.strip() else None,
                        "persona": new_persona.strip() if new_persona.strip() else None,
                        "assignment": new_assignment.strip() if new_assignment.strip() else None,
                        "output_type_ids": new_output_ids if st.session_state.output_types_for_templates else []
                    }
                    
                    try:
                        r = requests.put(f"{API}/templates/{row_data['id']}", json=payload)
                        if r.status_code == 200:
                            st.success("✅ Änderungen gespeichert!")
                            st.session_state.templates = requests.get(f"{API}/templates").json()
                            st.session_state.edit_template_mode = False
                            st.rerun()
                        else:
                            st.error(f"Fehler {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Fehler beim Speichern: {e}")
            
            with col_cancel:
                if st.button("❌ Abbrechen", key="cancel_template_edit"):
                    st.session_state.edit_template_mode = False
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️ Löschen", key="delete_template", type="secondary"):
                    try:
                        r = requests.delete(f"{API}/templates/{row_data['id']}")
                        if r.status_code == 200:
                            st.success(f"✅ '{row_data['name']}' gelöscht!")
                            st.session_state.templates = requests.get(f"{API}/templates").json()
                            st.session_state.show_template_form = False
                            st.session_state.selected_template_row = None
                            st.session_state.edit_template_mode = False
                            st.rerun()
                        else:
                            st.error(f"Fehler {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Fehler beim Löschen: {e}")
        else:
            if st.button("❌ Schließen", key="close_template_form"):
                st.session_state.show_template_form = False
                st.session_state.selected_template_row = None
                st.rerun()

# ========================================
# 3) Ergebnisse
# ========================================
with tabs[2]:
    st.header("Runs & Ergebnisse")
    
    # === SECTION 1: Neue Analyse starten ===
    st.subheader("🚀 Neue Analyse starten")
    
    # Template-Dropdown (außerhalb Form für reactive UI)
    try:
        tpl_response = requests.get(f"{API}/templates", timeout=2)
        templates = tpl_response.json() if tpl_response.status_code == 200 else []
    except:
        templates = []
        st.error("❌ Kann Templates nicht laden – API erreichbar?")
    
    if templates:
        tpl_options = {f"{t['id']} – {t['name']}": t['id'] for t in templates}
        selected_tpl = st.selectbox("Template wählen", options=list(tpl_options.keys()), key="run_tpl")
        template_id = tpl_options[selected_tpl]
        
        # Extra URLs
        extra_urls_raw = st.text_area("Zusätzliche URLs (eine pro Zeile, optional)", height=80, key="run_urls")
        extra_urls = [u.strip() for u in extra_urls_raw.split("\n") if u.strip()] if extra_urls_raw else []
        
        # KI-Einstellungen (außerhalb Form damit Provider-Wechsel sofort Modell aktualisiert)
        col1, col2, col3 = st.columns(3)
        with col1:
            ai_provider = st.selectbox("AI Provider", ["openai", "anthropic", "mistral"], key="run_provider")
        with col2:
            # Empfohlene Modelle je Provider - dynamisch basierend auf Provider
            model_map = {
                "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                "anthropic": ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"],
                "mistral": ["mistral-small-latest", "mistral-large-latest"]
            }
            ai_model = st.selectbox("AI Modell", model_map.get(ai_provider, ["gpt-4o-mini"]), key="run_model")
        with col3:
            ai_temperature = st.number_input("Temperature", 0.0, 1.0, 0.0, 0.1, key="run_temp")
        
        use_ai = st.checkbox("LLM-Analyse aktivieren", value=True, key="run_use_ai")
        
        # Submit-Button (kein Form mehr, damit UI sofort reagiert)
        submit = st.button("▶ Analyse starten", type="primary", key="submit_new_run")
        
        if submit:
            payload = {
                "template_id": template_id,
                "extra_urls": extra_urls if extra_urls else None,
                "ai_provider": ai_provider,
                "ai_model": ai_model,
                "ai_temperature": ai_temperature,
                "use_ai": use_ai
            }
            
            with st.spinner("⏳ Starte Analyse... (kann 10-30 Sek. dauern)"):
                try:
                    run_response = requests.post(f"{API}/runs", json=payload, timeout=60)
                    if run_response.status_code == 201:
                        new_run = run_response.json()
                        st.success(f"✓ Analyse gestartet! Run ID: {new_run['id']}")
                        st.balloons()
                    else:
                        st.error(f"Fehler {run_response.status_code}: {run_response.text[:300]}")
                except requests.exceptions.Timeout:
                    st.error("⏱ Timeout – Analyse dauert zu lange (>60s)")
                except Exception as e:
                    st.error(f"❌ Fehler: {e}")
    else:
        st.warning("Keine Templates vorhanden – erstelle zuerst ein Template im Tab 'Templates'")
    
    st.divider()
    
    # === SECTION 2: Vorhandene Runs anzeigen ===
    st.subheader("📊 Vorhandene Runs")
    
    if st.button("↻ Runs neu laden", key="reload_runs"):
        st.rerun()
    
    try:
        rl_response = requests.get(f"{API}/runs", timeout=2)
        rl = rl_response.json() if rl_response.status_code == 200 else []
        if not isinstance(rl, list):
            rl = []
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Verbindung zur API fehlgeschlagen!")
        st.info(f"Stelle sicher, dass die API läuft auf: {API}")
        rl = []
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        st.info("Stelle sicher, dass die API läuft: uvicorn newsapp.main:app --app-dir src")
        rl = []
    
    if rl and isinstance(rl, list) and len(rl) > 0:
        df = pd.DataFrame(rl)[["id","template_id","status","relevance_score","created_at","finished_at"]]
        
        # Interaktive Tabelle mit Row-Selection
        event = st.dataframe(
            df, 
            width="stretch", 
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="runs_table"
        )
        
        # Zeilen-Auswahl Handler
        selected_run_id = None
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_run_id = df.iloc[selected_idx]["id"]
        
        # Fallback: Dropdown wenn keine Zeile ausgewählt
        if not selected_run_id:
            rid = st.selectbox("Run Details anzeigen (oder Zeile in Tabelle klicken)", [r["id"] for r in rl], key="run_select")
        else:
            rid = selected_run_id
            st.info(f"📌 Run #{rid} ausgewählt (klicke andere Zeile für Wechsel)")
        
        if rid:
            try:
                r = requests.get(f"{API}/runs/{rid}").json()
                
                # Header mit Delete Button
                col_header, col_delete = st.columns([4, 1])
                with col_header:
                    st.subheader(f"Run #{rid} – Status: {r['status']}")
                with col_delete:
                    if st.button("🗑️ Löschen", key=f"delete_run_{rid}", type="secondary"):
                        try:
                            del_response = requests.delete(f"{API}/runs/{rid}")
                            if del_response.status_code == 200:
                                st.success(f"✅ Run #{rid} gelöscht!")
                                st.rerun()
                            else:
                                st.error(f"Fehler {del_response.status_code}: {del_response.text[:200]}")
                        except Exception as e:
                            st.error(f"Fehler beim Löschen: {e}")
                
                # Provider-Info anzeigen
                if r.get("summary") and r["summary"].get("ai_provider"):
                    st.info(f"🤖 KI-Provider: **{r['summary']['ai_provider']}** – Modell: **{r['summary']['ai_model']}**")
                
                # Warnung wenn Changes/Actions/Risks fehlen
                missing = []
                if not r.get("changes"): missing.append("Changes")
                if not r.get("actions"): missing.append("Actions")
                if not r.get("risks"): missing.append("Risks")
                if missing:
                    st.warning(f"⚠️ Fehlende Daten: {', '.join(missing)} – LLM hat diese nicht generiert oder Fehler aufgetreten")
                
                col1, col2 = st.columns(2)
                with col1: 
                    st.markdown("**Summary**")
                    st.json(r.get("summary") or {})
                
                with col2: 
                    st.markdown("**Details**")
                    st.json({
                        "changes": r.get("changes"),
                        "actions": r.get("actions"),
                        "risks": r.get("risks")
                    })
                
                st.markdown("**Findings per page**")
                st.json(r.get("findings_per_page") or {})
            except Exception as e:
                st.error(f"Fehler beim Laden von Run {rid}: {e}")
    else:
        st.info("Noch keine Runs vorhanden – starte eine Analyse oben!")

