from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Message(BaseModel):
    role: str  # "user" ou "assistant"
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    langue: Optional[str] = "fr"

class ChatResponse(BaseModel):
    session_id: str
    response: str
    session_data: Optional[dict] = None
    plan_ready: bool = False

class UserProfile(BaseModel):
    session_id: str
    langue: Optional[str] = "fr"
    region: Optional[str] = None
    ville: Optional[str] = None
    diplome: Optional[str] = None
    filiere: Optional[str] = None
    duree_chomage_mois: Optional[int] = None
    age: Optional[int] = None
    genre: Optional[str] = None
    situation_familiale: Optional[str] = None
    personnes_a_charge: Optional[bool] = None
    mobilite: Optional[bool] = None
    acces_internet: Optional[str] = None
    acces_ordinateur: Optional[bool] = None
    budget_formation_fcfa: Optional[int] = None
    type_objectif: Optional[str] = None
    secteur_interet: Optional[str] = None
    horizon_mois: Optional[int] = None

class PlanPhase(BaseModel):
    titre: str
    duree: str
    actions: List[str]
    objectif: str

class ReconversionPlan(BaseModel):
    session_id: str
    date_generation: str
    profil_resume: str
    inadéquation_principale: str
    cas_inspiration: Optional[str] = None
    phase_1: PlanPhase
    phase_2: PlanPhase
    phase_3: PlanPhase
    ressources: List[str]
    financements: List[str]
    score_progression: int = 0

class PlanExportRequest(BaseModel):
    session_id: str
    format: str = "json"  # "json" ou "pdf"

class SessionData(BaseModel):
    session_id: str
    messages: List[Message] = []
    profile: Optional[UserProfile] = None
    plan: Optional[ReconversionPlan] = None
    onboarding_step: int = 0
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()
