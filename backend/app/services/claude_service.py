import anthropic
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

def load_system_prompt() -> str:
    with open(KNOWLEDGE_DIR / "system_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

def load_knowledge_base() -> dict:
    kb = {}
    files = {
        "secteurs_formels": "bloc1a_secteurs_formels.json",
        "secteurs_informels": "bloc1b_secteurs_informels.json",
        "filieres": "bloc2a_filieres.json",
        "formations_structures": "bloc3_formations_structures.json",
        "regions_contraintes": "bloc4_regions_contraintes.json",
    }
    for key, filename in files.items():
        path = KNOWLEDGE_DIR / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                kb[key] = json.load(f)
    return kb

SYSTEM_PROMPT = load_system_prompt()
KNOWLEDGE_BASE = load_knowledge_base()

def build_context_prompt() -> str:
    """Injecte un résumé de la base de connaissances dans le contexte système."""
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

def chat_with_reorient(messages: list, session_data: dict = None) -> str:
    """
    Envoie un message à ReOrient CM et retourne la réponse.
    
    Args:
        messages: Liste de messages au format [{role: str, content: str}]
        session_data: Données de session optionnelles pour contextualiser
    
    Returns:
        str: Réponse de ReOrient CM
    """
    system = build_context_prompt()
    
    if session_data:
        session_context = f"\n\n---\nDONNÉES DE SESSION ACTUELLES :\n{json.dumps(session_data, ensure_ascii=False, indent=2)}\n---\n"
        system += session_context

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system,
        messages=messages
    )
    
    return response.content[0].text

def get_region_data(region_id: str) -> dict:
    """Retourne les données d'une région par son ID."""
    regions = KNOWLEDGE_BASE.get("regions_contraintes", {}).get("regions", [])
    for r in regions:
        if r["id"] == region_id or region_id.lower() in r["nom"].lower() or region_id.lower() in [v.lower() for v in r["villes_principales"]]:
            return r
    return {}

def get_filiere_data(filiere_id: str) -> dict:
    """Retourne les données d'une filière par son ID."""
    filieres = KNOWLEDGE_BASE.get("filieres", [])
    for f in filieres:
        if f["id"] == filiere_id or filiere_id.lower() in f["filiere"].lower():
            return f
    return {}

def get_formations_for_profile(budget_fcfa: int, has_computer: bool, region_id: str) -> list:
    """Retourne les formations adaptées au profil de l'utilisateur."""
    all_formations = KNOWLEDGE_BASE.get("formations_structures", {}).get("formations", [])
    filtered = []
    
    for f in all_formations:
        if budget_fcfa == 0 and "gratuit" not in f.get("acces", []):
            continue
        if not has_computer and f.get("cout_fcfa_min", 0) == 0:
            filtered.append(f)
        else:
            if f.get("cout_fcfa_min", 0) <= budget_fcfa:
                filtered.append(f)
    
    return filtered
