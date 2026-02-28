"""Combined FastAPI app - Module 1 + Module 4."""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from module1.database import init_db as init_db1
        init_db1()
        logger.info("✅ Module 1 DB initialized")
    except Exception as e:
        logger.error(f"Module 1 DB init failed: {e}")
    try:
        from module4.database import init_db as init_db4
        init_db4()
        logger.info("✅ Module 4 DB initialized")
    except Exception as e:
        logger.error(f"Module 4 DB init failed: {e}")
    yield


app = FastAPI(
    title="Rayeva AI Systems",
    description="Module 1 (Categories) + Module 4 (WhatsApp Bot)",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Rayeva AI Systems running"}


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


try:
    from module1.main import app as module1_app
    for route in module1_app.routes:
        if hasattr(route, 'path') and route.path not in ["/health", "/", "/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"]:
            app.add_api_route(
                path=route.path,
                endpoint=route.endpoint,
                methods=list(route.methods) if route.methods else ["GET"],
                tags=["Module 1"],
                summary=getattr(route, 'summary', None),
                response_model=getattr(route, 'response_model', None),
            )
    logger.info("✅ Module 1 loaded")
except Exception as e:
    import traceback
    logger.error(f"❌ Module 1 failed: {e}")
    logger.error(traceback.format_exc())


try:
    from module4.main import app as module4_app
    for route in module4_app.routes:
        if hasattr(route, 'path') and route.path not in ["/health", "/", "/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"]:
            app.add_api_route(
                path=route.path,
                endpoint=route.endpoint,
                methods=list(route.methods) if route.methods else ["GET"],
                tags=["Module 4 - WhatsApp"],
                summary=getattr(route, 'summary', None),
                response_model=getattr(route, 'response_model', None),
            )
    logger.info("✅ Module 4 loaded")
except Exception as e:
    import traceback
    logger.error(f"❌ Module 4 failed: {e}")
    logger.error(traceback.format_exc())