from typing import Dict, List
from datetime import datetime
import uuid

# Stockage des sessions en mémoire (suffisant pour la démo)
_sessions: Dict[str, dict] = {}

def create_session() -> str:
    """Crée une nouvelle session et retourne son ID."""
    session_id = str(uuid.uuid4())[:8]
    _sessions[session_id] = {
        "session_id": session_id,
        "messages": [],
        "profile": {},
        "plan": None,
        "onboarding_step": 0,
        "plan_ready": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    return session_id

def get_session(session_id: str) -> dict:
    """Récupère une session par son ID."""
    return _sessions.get(session_id, {})

def update_session(session_id: str, data: dict) -> bool:
    """Met à jour les données d'une session."""
    if session_id not in _sessions:
        return False
    _sessions[session_id].update(data)
    _sessions[session_id]["updated_at"] = datetime.now().isoformat()
    return True

def add_message(session_id: str, role: str, content: str) -> bool:
    """Ajoute un message à l'historique d'une session."""
    if session_id not in _sessions:
        return False
    _sessions[session_id]["messages"].append({
        "role": role,
        "content": content
    })
    _sessions[session_id]["updated_at"] = datetime.now().isoformat()
    return True

def get_messages(session_id: str) -> List[dict]:
    """Retourne l'historique des messages d'une session."""
    session = _sessions.get(session_id, {})
    return session.get("messages", [])

def update_profile(session_id: str, profile_data: dict) -> bool:
    """Met à jour le profil utilisateur dans la session."""
    if session_id not in _sessions:
        return False
    if "profile" not in _sessions[session_id]:
        _sessions[session_id]["profile"] = {}
    _sessions[session_id]["profile"].update(profile_data)
    _sessions[session_id]["updated_at"] = datetime.now().isoformat()
    return True

def set_plan(session_id: str, plan: dict) -> bool:
    """Enregistre le plan de reconversion dans la session."""
    if session_id not in _sessions:
        return False
    _sessions[session_id]["plan"] = plan
    _sessions[session_id]["plan_ready"] = True
    _sessions[session_id]["updated_at"] = datetime.now().isoformat()
    return True

def list_sessions() -> List[str]:
    """Liste tous les IDs de session actifs."""
    return list(_sessions.keys())

def delete_session(session_id: str) -> bool:
    """Supprime une session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
