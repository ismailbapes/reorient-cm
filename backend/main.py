from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.routers import chat, plan, auth, conversations
from app.database import init_db
import uvicorn
import os

app = FastAPI(
    title="ReOrient CM",
    description="Assistant IA de reconversion professionnelle pour les diplômés camerounais",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

app.include_router(auth.router,          prefix="/api", tags=["auth"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(chat.router,          prefix="/api", tags=["chat"])
app.include_router(plan.router,          prefix="/api", tags=["plan"])

# Frontend dans le même dossier backend/frontend/
FRONTEND = Path(__file__).parent / "frontend" / "index.html"

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def serve_root():
    return FileResponse(str(FRONTEND))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse(str(FRONTEND))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n========================================")
    print(f"  ReOrient CM — Serveur démarré")
    print(f"  Ouvrez : http://localhost:{port}")
    print(f"========================================\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
