# 🚀 Rayeva AI Systems

🔗 Live Demo (Swagger Docs):  
https://rayeva-ai-systems.onrender.com/docs

AI-powered backend system with:
- Module 1 — AI Product Categorization
- Module 4 — AI WhatsApp Support Bot# Rayeva AI Systems — Full Stack / AI Intern Assignment

AI-powered modules for sustainable commerce built with FastAPI, Groq AI (LLaMA 3.3 70B), and SQLite.

---

## Modules Implemented

### Module 1: AI Auto-Category & Tag Generator
Automatically categorizes products, generates SEO tags, and suggests sustainability filters using AI.

**Endpoint:** `POST /api/v1/categories/generate`

**Input:**
```json
{
  "product_name": "Bamboo Cutting Board",
  "product_description": "Eco-friendly bamboo cutting board, naturally antimicrobial",
  "product_price": 29.99
}
```

**Output:**
```json
{
  "product_id": 1,
  "primary_category": "Kitchen",
  "sub_category": "Cutting Boards",
  "seo_tags": ["Bamboo Products", "Eco-Friendly Kitchen", "Sustainable Cooking", "Antimicrobial Boards", "Kitchen Essentials"],
  "sustainability_filters": [
    {"name": "plastic-free", "confidence": 0.98},
    {"name": "organic", "confidence": 0.85}
  ]
}
```

---

### Module 4: AI WhatsApp Support Bot
Handles customer support messages, answers product queries using real database data, explains return policy, and escalates refund/complaint issues.
### 🔹 Example API Request (cURL)

curl -X POST "https://rayeva-ai-systems.onrender.com/module4/chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "Where is my order?"
}'
### 🔹 Example Response

{
  "intent": "order_status",
  "response": "Sure! Please provide your Order ID so I can check the status for you."
}
### 🔹 Escalation Handling

If the user message is unrelated or complex, the AI responds:

"I'm forwarding your request to a human support representative."

This ensures safe and controlled AI behavior.

**Endpoints:**
- `POST /api/v4/whatsapp/message` — Send a message, get AI response
- `GET /api/v4/whatsapp/conversations` — View all logged conversations
- `GET /api/v4/whatsapp/conversations?escalated_only=true` — View escalated issues

**Input:**
```json
{
  "customer_phone": "+911234567890",
  "message": "Do you have a Bamboo Cutting Board?"
}
```

**Output:**
```json
{
  "customer_phone": "+911234567890",
  "customer_message": "Do you have a Bamboo Cutting Board?",
  "bot_response": "Yes! We have the Bamboo Cutting Board (SKU: SKU-001) priced at $29.99...",
  "intent": "order_query",
  "escalated": false,
  "confidence": 0.95,
  "processing_time_ms": 843
}
```

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│            FastAPI Application          │
│                                         │
│  /api/v1/categories/generate  (M1)      │
│  /api/v4/whatsapp/message     (M4)      │
└────────────┬────────────────────────────┘
             │
    ┌────────▼────────┐
    │   Groq AI API   │
    │ LLaMA 3.3 70B   │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  SQLite Database│
    │  - products     │
    │  - ai_logs      │
    │  - whatsapp_    │
    │    conversations│
    └─────────────────┘
```

**Separation of AI and Business Logic:**
- `module1_category_generator.py` — AI logic for categorization
- `module4_whatsapp_bot.py` — AI logic for support bot
- `models.py` — Database models (business data)
- `schemas.py` — Input/output validation
- `database.py` — Database connection
- `config.py` — Environment and API key management

---

## AI Prompt Design

### Module 1 Prompt Strategy
- **Role:** Expert product categorization system
- **Constraint:** Returns ONLY valid JSON — no explanations
- **Categories:** Predefined list to prevent hallucination
- **Sustainability filters:** Strict allowed list with post-processing validation
- **Temperature:** 0.3 (low — for consistent, structured output)

### Module 4 Prompt Strategy
- **Role:** Raya, a friendly WhatsApp support assistant
- **Context injection:** Real product data from database is injected into every prompt
- **Intent detection:** AI returns intent tag (order_query, return_policy, escalate, general)
- **Escalation logic:** AI flags refund/complaint messages for human follow-up
- **Temperature:** 0.5 (balanced — friendly but consistent)

---

## Technical Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI |
| AI Model | Groq — LLaMA 3.3 70B Versatile |
| Database | SQLite + SQLAlchemy |
| Validation | Pydantic v2 |
| Config | pydantic-settings + .env |
| Server | Uvicorn |

---

## Setup Instructions

### Module 1
```bash
cd module1
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Add your GROQ_API_KEY to .env
python main.py
# Runs on http://localhost:8000/docs
```

### Module 4
```bash
cd module4
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Add your GROQ_API_KEY to .env
python main.py
# Runs on http://localhost:8001/docs
```

---

## Environment Variables

Create a `.env` file in each module folder:
```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./rayeva.db
ENVIRONMENT=development
DEBUG=True
```

Get a free Groq API key at: https://console.groq.com

---

## Module Architecture Outlines (Modules 2 & 3)

### Module 2: AI B2B Proposal Generator
- Input: client budget, industry, sustainability goals
- AI generates: product mix, budget allocation, cost breakdown, impact summary
- Output: structured JSON proposal stored in database

### Module 3: AI Impact Reporting Generator
- Input: order data from database
- AI estimates: plastic saved (kg), carbon avoided (kg CO2), local sourcing %
- Output: human-readable impact statement stored with order
