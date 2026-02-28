"""FastAPI Application - create web API."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from module1.database import get_db, init_db
from module1.schemas import CategoryGeneratorRequest, CategoryGeneratorResponse
from module1.module1_category_generator import generate_categories_and_tags
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="Rayeva AI Systems - Module 1",
    description="AI-powered product categorization",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Module 1 is running"}

@app.get("/")
async def root():
    return {"message": "Rayeva AI Systems - Module 1 is running", "docs": "/docs"}


@app.post("/api/v1/categories/generate", response_model=CategoryGeneratorResponse)
async def generate_categories(
    request: CategoryGeneratorRequest,
    db: Session = Depends(get_db)
):
    """Generate categories and tags for a product."""
    try:
        logger.info(f"Processing product: {request.product_name}")
        response = await generate_categories_and_tags(
            product_name=request.product_name,
            product_description=request.product_description,
            product_price=request.product_price,
            db=db
        )
        logger.info(f"Successfully processed product ID: {response.product_id}")
        return response
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
