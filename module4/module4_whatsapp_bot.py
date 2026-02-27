"""Module 4 - WhatsApp Support Bot using AI."""
import time
import json
from sqlalchemy.orm import Session
from groq import Groq
from config import get_settings
from models import Product, AILog

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)

# Return policy (business logic - not AI)
RETURN_POLICY = """
- Items can be returned within 30 days of purchase.
- Items must be unused and in original packaging.
- Refunds are processed within 5-7 business days.
- To initiate a return, contact support@rayeva.com.
- Sale items and perishable goods are non-returnable.
"""

SYSTEM_PROMPT = """You are Raya, a friendly WhatsApp support assistant for Rayeva — a sustainable commerce platform.

You will receive a customer message and some context (product/order data from the database).
Respond in a helpful, concise, WhatsApp-friendly tone (short paragraphs, no bullet lists).

Rules:
1. For order/product queries: use the provided database context to answer accurately.
2. For return policy questions: use the provided return policy text.
3. For refund requests or complaints: respond empathetically and flag as ESCALATE.
4. For anything else: answer helpfully or say you'll connect them with the team.

Always end your response with a JSON block on a new line in this exact format:
{"intent": "order_query|return_policy|escalate|general", "escalate": true|false, "confidence": 0.0-1.0}
"""


def get_database_context(message: str, db: Session) -> str:
    """Pull relevant data from database based on message."""
    context_parts = []

    # Search for product mentions in message
    products = db.query(Product).all()
    message_lower = message.lower()

    matched_products = [
        p for p in products
        if p.name and p.name.lower() in message_lower
        or (p.sku and p.sku.lower() in message_lower)
    ]

    if matched_products:
        context_parts.append("Relevant products found in database:")
        for p in matched_products[:3]:
            context_parts.append(
                f"- {p.name} (SKU: {p.sku}) | Price: ${p.price} | "
                f"Category: {p.primary_category or 'N/A'} | "
                f"Sub-category: {p.sub_category or 'N/A'}"
            )
    else:
        # Return summary of available products
        total = db.query(Product).count()
        context_parts.append(f"Total products in catalog: {total}")
        recent = db.query(Product).order_by(Product.created_at.desc()).limit(3).all()
        if recent:
            context_parts.append("Recent products:")
            for p in recent:
                context_parts.append(f"- {p.name} (SKU: {p.sku}) | Price: ${p.price}")

    return "\n".join(context_parts) if context_parts else "No specific product data found."


def parse_ai_response(response_text: str) -> tuple[str, dict]:
    """Split AI message from the JSON metadata block."""
    metadata = {"intent": "general", "escalate": False, "confidence": 0.8}

    try:
        # Find the last JSON block
        last_brace = response_text.rfind("{")
        if last_brace != -1:
            json_str = response_text[last_brace:]
            end_brace = json_str.find("}") + 1
            metadata = json.loads(json_str[:end_brace])
            message = response_text[:last_brace].strip()
        else:
            message = response_text
    except (json.JSONDecodeError, ValueError):
        message = response_text

    return message, metadata


async def handle_whatsapp_message(
    customer_message: str,
    customer_phone: str,
    db: Session
) -> dict:
    """
    Main function - receives WhatsApp message, calls AI, returns response.
    """
    start_time = time.time()

    # STEP 1: Get relevant database context
    db_context = get_database_context(customer_message, db)

    # STEP 2: Build prompt
    user_prompt = f"""Customer phone: {customer_phone}
Customer message: {customer_message}

--- Database Context ---
{db_context}

--- Return Policy ---
{RETURN_POLICY}

Respond to the customer now."""

    input_data = {
        "customer_phone": customer_phone,
        "customer_message": customer_message,
    }

    try:
        # STEP 3: Call Groq AI
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        raw_response = response.choices[0].message.content.strip()

        # STEP 4: Parse response and metadata
        bot_message, metadata = parse_ai_response(raw_response)

        # STEP 5: Log the conversation
        processing_time_ms = int((time.time() - start_time) * 1000)
        log_entry = AILog(
            module_name="Module 4: WhatsApp Support Bot",
            input_data=input_data,
            prompt=user_prompt,
            ai_response={"message": bot_message, "metadata": metadata},
            tokens_used=response.usage.total_tokens,
            processing_time_ms=processing_time_ms,
            status="success"
        )
        db.add(log_entry)
        db.commit()

        # STEP 6: Return structured response
        return {
            "customer_phone": customer_phone,
            "customer_message": customer_message,
            "bot_response": bot_message,
            "intent": metadata.get("intent", "general"),
            "escalated": metadata.get("escalate", False),
            "confidence": metadata.get("confidence", 0.8),
            "processing_time_ms": processing_time_ms
        }

    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        log_entry = AILog(
            module_name="Module 4: WhatsApp Support Bot",
            input_data=input_data,
            prompt=user_prompt,
            ai_response={},
            processing_time_ms=processing_time_ms,
            status="error",
            error_message=str(e)
        )
        db.add(log_entry)
        db.commit()
        raise
