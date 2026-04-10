from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.claude_service import chat_with_reorient
from app.services.session_manager import (
    create_session, get_session, add_message, get_messages, update_session
)

router = APIRouter()

@router.post("/session/new")
async def new_session(body: dict = None):
    """Crée une nouvelle session de conversation."""
    session_id = create_session()
    langue = (body or {}).get("langue", "fr")

    welcome_fr = """Bonjour ! Je suis **ReOrient CM**, un assistant spécialisé dans la reconversion et l'orientation professionnelle pour les diplômés camerounais.

Je suis là pour t'aider — pas avec des conseils génériques, mais avec des pistes concrètes adaptées à ta situation réelle au Cameroun.

Dis-moi ce qui t'amène. Parle-moi de toi, de ta situation, de ce que tu vis — **je t'écoute.**"""

    welcome_en = """Hello! I'm **ReOrient CM**, an assistant specialized in professional reorientation for Cameroonian graduates.

I'm here to help you — not with generic advice, but with concrete options adapted to your real situation in Cameroon.

Tell me what brings you here. Talk to me about yourself, your situation, what you're going through — **I'm listening.**"""

    welcome = welcome_en if langue == "en" else welcome_fr
    add_message(session_id, "assistant", welcome)

    return {
        "session_id": session_id,
        "message": welcome,
        "status": "started"
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Envoie un message et reçoit la réponse de ReOrient CM."""
    session = get_session(request.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable. Créez une nouvelle session avec /api/session/new")
    
    # Ajouter le message de l'utilisateur
    add_message(request.session_id, "user", request.message)
    
    # Récupérer l'historique complet
    messages = get_messages(request.session_id)
    
    # Obtenir la réponse de Claude
    response_text = chat_with_reorient(
        messages=messages,
        session_data=session.get("profile", {})
    )
    
    # Ajouter la réponse à l'historique
    add_message(request.session_id, "assistant", response_text)
    
    # Détecter si le plan est prêt (présence des 3 phases dans la réponse)
    plan_ready = (
        "PHASE 1" in response_text and
        "PHASE 2" in response_text and
        "PHASE 3" in response_text
    )
    
    if plan_ready:
        update_session(request.session_id, {
            "plan_ready": True,
            "plan_text": response_text
        })
    
    return ChatResponse(
        session_id=request.session_id,
        response=response_text,
        session_data=session.get("profile", {}),
        plan_ready=plan_ready
    )

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Récupère les informations d'une session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return session

@router.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Récupère l'historique des messages d'une session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return {"session_id": session_id, "messages": get_messages(session_id)}
