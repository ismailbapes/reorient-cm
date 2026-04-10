from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.database import get_db, Conversation, Message
from app.services.auth_service import get_current_user
from app.database import User

router = APIRouter()


@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste toutes les conversations de l'utilisateur connecté."""
    convs = db.query(Conversation)\
        .filter(Conversation.user_id == current_user.id)\
        .order_by(desc(Conversation.updated_at))\
        .all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "langue": c.langue,
            "session_id": c.session_id,
            "plan_ready": c.plan_ready,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
            "msg_count": len(c.messages)
        }
        for c in convs
    ]


@router.post("/conversations")
async def create_conversation(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle conversation."""
    conv = Conversation(
        user_id=current_user.id,
        title=body.get("title", "Nouvelle conversation"),
        langue=body.get("langue", "fr"),
        session_id=body.get("session_id")
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "title": conv.title, "langue": conv.langue, "session_id": conv.session_id}


@router.get("/conversations/{conv_id}/messages")
async def get_messages(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les messages d'une conversation."""
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    return {
        "conversation_id": conv_id,
        "messages": [
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in conv.messages
        ]
    }


@router.post("/conversations/{conv_id}/messages")
async def add_message(
    conv_id: str,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute un message à une conversation."""
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    msg = Message(
        conversation_id=conv_id,
        role=body.get("role", "user"),
        content=body.get("content", "")
    )
    db.add(msg)

    # Mise à jour titre depuis le premier message utilisateur
    user_msgs = [m for m in conv.messages if m.role == "user"]
    if body.get("role") == "user" and len(user_msgs) == 0:
        raw = body.get("content", "").replace("[Date du jour", "").split("]")[-1].strip()
        conv.title = raw[:42] or "Nouvelle conversation"

    # Mise à jour session_id et plan_ready
    if body.get("session_id"):
        conv.session_id = body["session_id"]
    if body.get("plan_ready"):
        conv.plan_ready = True

    conv.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "title": conv.title}


@router.patch("/conversations/{conv_id}")
async def update_conversation(
    conv_id: str,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour les métadonnées d'une conversation."""
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    if "title" in body:
        conv.title = body["title"]
    if "session_id" in body:
        conv.session_id = body["session_id"]
    if "plan_ready" in body:
        conv.plan_ready = body["plan_ready"]

    conv.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}


@router.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime une conversation et tous ses messages."""
    conv = db.query(Conversation).filter(
        Conversation.id == conv_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    db.delete(conv)
    db.commit()
    return {"ok": True}
