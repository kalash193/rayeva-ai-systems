"""Module 1 - Category Generator using AI."""
import json
import time
from sqlalchemy.orm import Session
from groq import Groq
from module1.config import get_settings
from module1.models import Product, AILog
from module1.schemas import CategoryGeneratorResponse, SustainabilityFilter

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)

# Instructions for AI
SYSTEM_PROMPT = """You are an expert product categorization system.

Analyze the product and return ONLY valid JSON:
{
    "primary_category": "one of: Electronics, Home & Garden, Fashion, Beauty, Sports, Kitchen, Office, Pet, Baby, Books",
    "sub_category": "specific subcategory",
    "seo_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "sustainability_filters": [
        {"name": "filter_name", "confidence": 0.95}
    ]
}

Sustainability filters must be from: plastic-free, compostable, vegan, recycled, organic, cruelty-free, fair-trade, energy-efficient.

Include 5 SEO tags and 2-4 sustainability filters.

IMPORTANT: Return ONLY the JSON object. No explanations."""

# Allowed sustainability filter values
ALLOWED_SUSTAINABILITY_FILTERS = {
    "plastic-free", "compostable", "vegan", "recycled",
    "organic", "cruelty-free", "fair-trade", "energy-efficient"
}


async def generate_categories_and_tags(
    product_name: str,
    product_description: str,
    product_price: float,
    db: Session
) -> CategoryGeneratorResponse:
    """
    Main function - takes product info, calls AI, saves to database.
    """
    start_time = time.time()

    # STEP 1: Create product in database
    product = Product(
        sku=f"SKU-{int(time.time())}",
        name=product_name,
        description=product_description,
        price=product_price,
        ai_processed=0
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # STEP 2: Build prompt for AI
    user_prompt = f"""
    Product Name: {product_name}
    Product Description: {product_description}
    Product Price: ${product_price}

    Please analyze this product and return categories, tags, and sustainability filters.
    """

    input_data = {
        "product_id": product.id,
        "product_name": product_name,
        "product_description": product_description,
        "product_price": product_price
    }

    try:
        # STEP 3: Call Groq AI
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        response_text = response.choices[0].message.content.strip()

        # STEP 4: Clean up response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()

        # STEP 5: Parse JSON
        ai_response_json = json.loads(response_text)

        # STEP 5b: Validate sustainability filters - strip any not in allowed list
        ai_response_json["sustainability_filters"] = [
            f for f in ai_response_json["sustainability_filters"]
            if f.get("name", "").lower() in ALLOWED_SUSTAINABILITY_FILTERS
        ]

        # STEP 6: Update product with AI results
        product.primary_category = ai_response_json["primary_category"]
        product.sub_category = ai_response_json["sub_category"]
        product.seo_tags = ai_response_json["seo_tags"]
        product.sustainability_filters = ai_response_json["sustainability_filters"]
        product.ai_processed = 1
        db.commit()

        # STEP 7: Log the request
        processing_time_ms = int((time.time() - start_time) * 1000)
        log_entry = AILog(
            module_name="Module 1: Category Generator",
            input_data=input_data,
            prompt=user_prompt,
            ai_response=ai_response_json,
            tokens_used=response.usage.total_tokens,
            processing_time_ms=processing_time_ms,
            status="success"
        )
        db.add(log_entry)
        db.commit()

        # STEP 8: Return response
        sustainability_filters = [
            SustainabilityFilter(**f)
            for f in ai_response_json["sustainability_filters"]
        ]

        return CategoryGeneratorResponse(
            product_id=product.id,
            primary_category=ai_response_json["primary_category"],
            sub_category=ai_response_json["sub_category"],
            seo_tags=ai_response_json["seo_tags"],
            sustainability_filters=sustainability_filters
        )

    except json.JSONDecodeError as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        log_entry = AILog(
            module_name="Module 1",
            input_data=input_data,
            prompt=user_prompt,
            ai_response={},
            processing_time_ms=processing_time_ms,
            status="error",
            error_message=f"JSON Parse Error: {str(e)}"
        )
        db.add(log_entry)
        db.commit()
        raise ValueError(f"AI response was not valid JSON: {str(e)}")

    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        log_entry = AILog(
            module_name="Module 1",
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
