from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.session_manager import get_session
from app.services.claude_service import chat_with_reorient
import io
import json
from datetime import datetime

router = APIRouter()

@router.get("/plan/{session_id}")
async def get_plan(session_id: str):
    """Récupère le plan de reconversion d'une session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")
    
    if not session.get("plan_ready"):
        return {
            "status": "not_ready",
            "message": "Le plan n'est pas encore généré. Complétez d'abord les questions d'onboarding."
        }
    
    return {
        "session_id": session_id,
        "plan_text": session.get("plan_text", ""),
        "profile": session.get("profile", {}),
        "generated_at": session.get("updated_at")
    }

@router.get("/plan/{session_id}/export")
async def export_plan(session_id: str, format: str = "json"):
    """Exporte le plan de reconversion en JSON ou PDF."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")
    
    if not session.get("plan_ready"):
        raise HTTPException(status_code=400, detail="Plan non disponible")
    
    if format == "json":
        export_data = {
            "reorient_cm": {
                "version": "1.0.0",
                "date_export": datetime.now().isoformat(),
                "session_id": session_id,
                "profil": session.get("profile", {}),
                "plan": session.get("plan_text", ""),
                "messages_count": len(session.get("messages", []))
            }
        }
        content = json.dumps(export_data, ensure_ascii=False, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=reorient_plan_{session_id}.json"}
        )
    
    elif format == "pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import cm
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            styles = getSampleStyleSheet()
            green = HexColor("#1D9E75")
            
            title_style = ParagraphStyle(
                "Title",
                parent=styles["Heading1"],
                textColor=green,
                fontSize=18,
                spaceAfter=12
            )
            
            heading_style = ParagraphStyle(
                "Heading",
                parent=styles["Heading2"],
                textColor=green,
                fontSize=13,
                spaceAfter=8
            )
            
            body_style = ParagraphStyle(
                "Body",
                parent=styles["Normal"],
                fontSize=11,
                spaceAfter=6,
                leading=16
            )
            
            story = []
            
            # En-tête
            story.append(Paragraph("ReOrient CM", title_style))
            story.append(Paragraph("Plan de Reconversion Professionnelle Personnalisé", heading_style))
            story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y')}", body_style))
            story.append(Spacer(1, 0.5*cm))
            
            # Contenu du plan
            plan_text = session.get("plan_text", "Plan non disponible")
            
            # Convertir le texte en paragraphes formatés
            for line in plan_text.split("\n"):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 0.3*cm))
                    continue
                
                # Nettoyer les émojis et caractères spéciaux pour PDF
                line = line.replace("🔍", "").replace("⚠️", "").replace("✅", "").replace("📋", "").replace("💰", "").replace("❓", "").replace("→", "-")
                
                if line.startswith("PHASE") or line.startswith("**"):
                    line = line.replace("**", "")
                    story.append(Paragraph(line, heading_style))
                elif line.startswith("-"):
                    story.append(Paragraph(f"• {line[1:].strip()}", body_style))
                else:
                    story.append(Paragraph(line, body_style))
            
            # Pied de page
            story.append(Spacer(1, cm))
            story.append(Paragraph(
                "Ce plan a été généré par ReOrient CM — Assistant IA de reconversion professionnelle pour diplômés camerounais.",
                ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9, textColor=HexColor("#888888"))
            ))
            
            doc.build(story)
            buffer.seek(0)
            
            return StreamingResponse(
                buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=reorient_plan_{session_id}.pdf"}
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur génération PDF : {str(e)}")
    
    else:
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'json' ou 'pdf'.")
