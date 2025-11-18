import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document
from schemas import Inquiry

app = FastAPI(title="Budapest Garden Services API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Budapest Garden Services API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Static content for services offered in Budapest
@app.get("/api/services")
def list_services():
    services = [
        {
            "id": 1,
            "title": "Garden Design",
            "description": "Tailored garden concepts inspired by Budapest's courtyards and terraces.",
            "icon": "sprout"
        },
        {
            "id": 2,
            "title": "Seasonal Maintenance",
            "description": "Pruning, lawn care, fertilizing and clean-ups throughout the year.",
            "icon": "leaf"
        },
        {
            "id": 3,
            "title": "Balcony & Rooftop",
            "description": "Compact green oases for apartments with irrigation and planters.",
            "icon": "flower"
        },
        {
            "id": 4,
            "title": "Irrigation Systems",
            "description": "Smart, water‑efficient drip and sprinkler systems installation.",
            "icon": "droplet"
        },
        {
            "id": 5,
            "title": "Planting & Turf",
            "description": "Soil preparation, planting palettes, instant turf, and mulch.",
            "icon": "trees"
        }
    ]
    return {"services": services}

# Contact / inquiry endpoint (persists to MongoDB)
@app.post("/api/inquiries")
def create_inquiry(payload: Inquiry):
    try:
        inserted_id = create_document("inquiry", payload)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
