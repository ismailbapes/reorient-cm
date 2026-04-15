from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db, User
from app.services.auth_service import hash_password, verify_password, create_token, get_current_user

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    nom: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/auth/register")
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur."""
    # Vérifier que l'email n'existe pas déjà
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
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "nom": user.nom},
        "message": "Compte créé avec succès"
    }


@router.post("/auth/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur existant."""
    user = db.query(User).filter(User.email == body.email.lower().strip()).first()

    if not user or not verify_password(body.password, user.hashed_pw):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")

    token = create_token(user.id)
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "nom": user.nom},
        "message": "Connexion réussie"
    }


@router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Récupère les infos de l'utilisateur connecté."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom": current_user.nom,
        "created_at": current_user.created_at.isoformat()
    }


@router.post("/auth/logout")
async def logout():
    """Déconnexion (le client supprime le token)."""
    return {"message": "Déconnecté avec succès"}
