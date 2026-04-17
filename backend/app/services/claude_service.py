import anthropic
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

def load_system_prompt() -> str:
    with open(KNOWLEDGE_DIR / "system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

def load_knowledge_base() -> dict:
    kb = {}
    files = {
        "secteurs_formels":    "bloc1a_secteurs_formels.json",
        "secteurs_informels":  "bloc1b_secteurs_informels.json",
        "filieres":            "bloc2a_filieres.json",
        "formations_structures": "bloc3_formations_structures.json",
        "regions_contraintes": "bloc4_regions_contraintes.json",
    }
    for key, filename in files.items():
        path = KNOWLEDGE_DIR / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                kb[key] = json.load(f)
    return kb

SYSTEM_PROMPT    = load_system_prompt()
KNOWLEDGE_BASE   = load_knowledge_base()

def build_context_prompt() -> str:
    kb_summary = f"""
---
DONNÉES DE LA BASE DE CONNAISSANCES CHARGÉES :

Secteurs formels disponibles : {[s['secteur'] for s in KNOWLEDGE_BASE.get('secteurs_formels', [])]}
Secteurs informels disponibles : {[s['secteur'] for s in KNOWLEDGE_BASE.get('secteurs_informels', [])]}
Filières universitaires : {[f['filiere'] for f in KNOWLEDGE_BASE.get('filieres', [])]}
Régions camerounaises avec indices d'opportunité : {[(r['nom'], r['indice_opportunite']) for r in KNOWLEDGE_BASE.get('regions_contraintes', {}).get('regions', [])]}
Structures d'appui : {[s['nom'] for s in KNOWLEDGE_BASE.get('formations_structures', {}).get('structures_appui', [])]}
---
"""
    return SYSTEM_PROMPT + kb_summary

def get_client() -> anthropic.Anthropic:
    """Crée un client Anthropic avec la clé API lue à chaque appel."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY manquante ou vide")
    return anthropic.Anthropic(api_key=api_key)

def chat_with_reorient(messages: list, session_data: dict = None) -> str:
    system = build_context_prompt()

    if session_data:
        session_context = f"\n\n---\nDONNÉES DE SESSION ACTUELLES :\n{json.dumps(session_data, ensure_ascii=False, indent=2)}\n---\n"
        system += session_context

    # Client créé à chaque requête pour lire la clé fraîche
    client = get_client()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system,
        messages=messages
    )

    return response.content[0].text
