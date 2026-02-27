"""FastAPI Application - Module 4: WhatsApp Support Bot."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, init_db
from schemas import WhatsAppMessageRequest, WhatsAppMessageResponse
from module4_whatsapp_bot import handle_whatsapp_message
from models import WhatsAppConversation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="Rayeva AI Systems - Module 4",
    description="AI-powered WhatsApp Support Bot",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Module 4 WhatsApp Bot is running"}


@app.post("/api/v4/whatsapp/message", response_model=WhatsAppMessageResponse)
async def whatsapp_message(
    request: WhatsAppMessageRequest,
    db: Session = Depends(get_db)
):
    """Handle incoming WhatsApp customer message and return AI response."""
    try:
        logger.info(f"[Module 4] Message from: {request.customer_phone}")
        result = await handle_whatsapp_message(
            customer_message=request.message,
            customer_phone=request.customer_phone,
            db=db
        )
        convo = WhatsAppConversation(
            customer_phone=result["customer_phone"],
            customer_message=result["customer_message"],
            bot_response=result["bot_response"],
            intent=result["intent"],
            escalated=result["escalated"],
            confidence=result["confidence"],
            processing_time_ms=result["processing_time_ms"]
        )
        db.add(convo)
        db.commit()

        if result["escalated"]:
            logger.warning(f"[Module 4] ESCALATED - phone: {request.customer_phone}")

        return WhatsAppMessageResponse(**result)

    except Exception as e:
        logger.error(f"[Module 4] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/whatsapp/conversations")
async def get_conversations(
    escalated_only: bool = False,
    db: Session = Depends(get_db)
):
    """View all logged WhatsApp conversations."""
    query = db.query(WhatsAppConversation)
    if escalated_only:
        query = query.filter(WhatsAppConversation.escalated == True)
    conversations = query.order_by(WhatsAppConversation.created_at.desc()).limit(50).all()
    return {"total": len(conversations), "conversations": [
        {
            "id": c.id,
            "phone": c.customer_phone,
            "message": c.customer_message,
            "response": c.bot_response,
            "intent": c.intent,
            "escalated": c.escalated,
            "confidence": c.confidence,
            "created_at": str(c.created_at)
        } for c in conversations
    ]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
