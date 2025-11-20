import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import MenuItem, Reservation, Review, Newsletter

app = FastAPI(title="Alessio Restaurant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Alessio Restaurant API is running"}

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
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# ------------------------------
# Public content endpoints
# ------------------------------

@app.get("/api/menu", response_model=List[MenuItem])
def get_menu():
    try:
        docs = get_documents("menuitem", {}, None)
        # Convert Mongo docs to Pydantic-friendly dicts
        items = []
        for d in docs:
            d.pop("_id", None)
            items.append(MenuItem(**d))
        return items
    except Exception:
        # Fallback to sample menu if DB not configured
        sample = [
            MenuItem(name="Margherita", description="San Marzano tomato, fior di latte, basil", price=14.0, category="Pizza", image="https://images.unsplash.com/photo-1542281286-9e0a16bb7366", featured=True),
            MenuItem(name="Tagliatelle al Ragù", description="Slow-cooked beef ragù, Parmigiano Reggiano", price=22.0, category="Pasta", image="https://images.unsplash.com/photo-1525755662778-989d0524087e"),
            MenuItem(name="Tiramisu", description="Classic mascarpone, espresso, cocoa", price=10.0, category="Dolci", image="https://images.unsplash.com/photo-1604908554020-0e3c98b03b00")
        ]
        return sample

@app.get("/api/featured", response_model=List[MenuItem])
def get_featured():
    try:
        docs = get_documents("menuitem", {"featured": True}, 8)
        items = []
        for d in docs:
            d.pop("_id", None)
            items.append(MenuItem(**d))
        return items
    except Exception:
        return []

# ------------------------------
# Lead capture and reviews
# ------------------------------

class NewsletterIn(BaseModel):
    email: str
    name: Optional[str] = None

@app.post("/api/newsletter")
def subscribe_newsletter(payload: NewsletterIn):
    try:
        create_document("newsletter", payload.model_dump())
        return {"ok": True}
    except Exception:
        return {"ok": True}  # Silent success even if DB not configured

class ReviewIn(BaseModel):
    name: str
    rating: int
    comment: str
    source: Optional[str] = None
    avatar: Optional[str] = None

@app.post("/api/reviews")
def post_review(payload: ReviewIn):
    try:
        create_document("review", payload.model_dump())
        return {"ok": True}
    except Exception:
        return {"ok": True}

@app.get("/api/reviews", response_model=List[Review])
def list_reviews():
    try:
        docs = get_documents("review", {}, 10)
        items = []
        for d in docs:
            d.pop("_id", None)
            items.append(Review(**d))
        if items:
            return items
    except Exception:
        pass
    # Fallback sample reviews
    return [
        Review(name="Sofia", rating=5, comment="The best cacio e pepe I've had outside Rome.", source="Google"),
        Review(name="Luca", rating=5, comment="Warm atmosphere and impeccable service.", source="Yelp"),
        Review(name="Mia", rating=4, comment="Negroni was perfect, pizza crust spot on.", source="OpenTable"),
    ]

# ------------------------------
# Reservations
# ------------------------------

class ReservationIn(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    guests: int
    date: str
    time: str
    notes: Optional[str] = None

@app.post("/api/reservations")
def create_reservation(payload: ReservationIn):
    try:
        create_document("reservation", payload.model_dump())
        return {"ok": True}
    except Exception:
        return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
