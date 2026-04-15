from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import os
import resend
from app.database import get_db, User, PasswordResetToken
from app.services.auth_service import hash_password, verify_password, create_token, get_current_user

router = APIRouter()

resend.api_key = os.environ.get("RESEND_API_KEY", "").strip()
APP_URL = os.environ.get("APP_URL", "http://localhost:8000").strip()
FROM_EMAIL = os.environ.get("FROM_EMAIL", "onboarding@resend.dev").strip()


class RegisterRequest(BaseModel):
    email: str
    nom: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str
    langue: str = "fr"


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/auth/register")
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email.lower().strip()).first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères")
    if len(body.nom.strip()) < 2:
        raise HTTPException(status_code=400, detail="Le nom doit contenir au moins 2 caractères")
    user = User(
        email=body.email.lower().strip(),
        nom=body.nom.strip(),
        hashed_pw=hash_password(body.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id)
    return {"token": token, "user": {"id": user.id, "email": user.email, "nom": user.nom}}


@router.post("/auth/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if not user or not verify_password(body.password, user.hashed_pw):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    token = create_token(user.id)
    return {"token": token, "user": {"id": user.id, "email": user.email, "nom": user.nom}}


@router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "nom": current_user.nom}


@router.post("/auth/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if not user:
        return {"message": "Si cet email existe, un lien a été envoyé."}

    # Invalider anciens tokens
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})
    db.commit()

    # Créer token valable 30 minutes
    raw_token = secrets.token_urlsafe(32)
    reset = PasswordResetToken(
        user_id=user.id,
        token=raw_token,
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(reset)
    db.commit()

    reset_url = f"{APP_URL}/reset-password?token={raw_token}"

    if body.langue == "en":
        subject = "ReOrient CM — Reset your password"
        html_content = f"""
        <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:40px 24px;background:#F4F3EF;">
          <div style="background:#fff;border-radius:16px;padding:36px;border:1px solid rgba(0,0,0,0.08);">
            <div style="margin-bottom:24px;">
              <span style="width:36px;height:36px;background:#1D9E75;border-radius:9px;display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:16px;padding:8px;">R</span>
              <span style="font-weight:700;font-size:18px;color:#085041;margin-left:8px;">ReOrient CM</span>
            </div>
            <h2 style="color:#18181A;font-size:20px;margin-bottom:12px;">Reset your password</h2>
            <p style="color:#6B6A68;font-size:15px;line-height:1.7;margin-bottom:24px;">
              Hello <strong>{user.nom}</strong>,<br><br>
              You requested a password reset. Click the button below — this link is valid for <strong>30 minutes</strong>.
            </p>
            <a href="{reset_url}" style="display:inline-block;padding:13px 28px;background:#1D9E75;color:#fff;border-radius:11px;text-decoration:none;font-weight:700;font-size:15px;margin-bottom:24px;">
              Reset my password
            </a>
            <p style="color:#6B6A68;font-size:13px;">If you did not request this, ignore this email.</p>
          </div>
        </div>"""
    else:
        subject = "ReOrient CM — Réinitialisez votre mot de passe"
        html_content = f"""
        <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:40px 24px;background:#F4F3EF;">
          <div style="background:#fff;border-radius:16px;padding:36px;border:1px solid rgba(0,0,0,0.08);">
            <div style="margin-bottom:24px;">
              <span style="width:36px;height:36px;background:#1D9E75;border-radius:9px;display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:16px;padding:8px;">R</span>
              <span style="font-weight:700;font-size:18px;color:#085041;margin-left:8px;">ReOrient CM</span>
            </div>
            <h2 style="color:#18181A;font-size:20px;margin-bottom:12px;">Réinitialisation de votre mot de passe</h2>
            <p style="color:#6B6A68;font-size:15px;line-height:1.7;margin-bottom:24px;">
              Bonjour <strong>{user.nom}</strong>,<br><br>
              Vous avez demandé une réinitialisation de mot de passe. Cliquez ci-dessous — ce lien est valable <strong>30 minutes</strong>.
            </p>
            <a href="{reset_url}" style="display:inline-block;padding:13px 28px;background:#1D9E75;color:#fff;border-radius:11px;text-decoration:none;font-weight:700;font-size:15px;margin-bottom:24px;">
              Réinitialiser mon mot de passe
            </a>
            <p style="color:#6B6A68;font-size:13px;">Si vous n'avez pas fait cette demande, ignorez cet email.</p>
          </div>
        </div>"""

    try:
        api_key = os.environ.get("RESEND_API_KEY", "").strip()
        resend.api_key = api_key
        params = {
            "from": FROM_EMAIL,
            "to": [user.email],
            "subject": subject,
            "html": html_content
        }
        result = resend.Emails.send(params)
        print(f"Email envoyé: {result}")
    except Exception as e:
        print(f"Erreur envoi email: {e}")

    return {"message": "Si cet email existe, un lien a été envoyé."}


@router.post("/auth/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == body.token,
        PasswordResetToken.used == False
    ).first()
    if not reset:
        raise HTTPException(status_code=400, detail="Lien invalide ou déjà utilisé.")
    if datetime.utcnow() > reset.expires_at:
        raise HTTPException(status_code=400, detail="Ce lien a expiré. Faites une nouvelle demande.")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères.")
    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    user.hashed_pw = hash_password(body.new_password)
    reset.used = True
    db.commit()
    return {"message": "Mot de passe mis à jour avec succès."}


@router.post("/auth/logout")
async def logout():
    return {"message": "Déconnecté"}
