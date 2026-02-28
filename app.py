"""Combined FastAPI app - Module 1 + Module 4."""
from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create main app
app = FastAPI(
    title="Rayeva AI Systems",
    description="Module 1 (Categories) + Module 4 (WhatsApp Bot)",
    version="1.0.0"
)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Rayeva AI Systems running"}

# Root
@app.get("/")
async def root():
    return {
        "message": "Rayeva AI Systems - Full Stack Implementation",
        "modules": [
            "Module 1: POST /api/v1/categories/generate (Product Categorization)",
            "Module 4: POST /api/v4/whatsapp/message (WhatsApp Support Bot)"
        ],
        "docs": "/docs"
    }

# Module 1 - Import and include routes
try:
    from module1.main import app as module1_app
    
    # Get Module 1 routes
    for route in module1_app.routes:
        if route.path not in ["/health", "/"]:
            app.routes.append(route)
    
    logger.info("✅ Module 1 loaded")
except Exception as e:
    logger.error(f"❌ Module 1 failed: {e}")

# Module 4 - Import and include routes
try:
    from module4.main import app as module4_app
    
    # Get Module 4 routes
    for route in module4_app.routes:
        if route.path not in ["/health"]:
            app.routes.append(route)
    
    logger.info("✅ Module 4 loaded")
except Exception as e:
    logger.error(f"❌ Module 4 failed: {e}")#force redeploy 
