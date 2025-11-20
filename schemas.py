"""
Database Schemas for Alessio Restaurant

Each Pydantic model represents a collection in your database.
Collection name is the lowercase class name.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Core domain models

class MenuItem(BaseModel):
    """
    Menu items offered by the restaurant
    Collection: "menuitem"
    """
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="e.g., Antipasti, Pasta, Pizza, Secondi, Dolci")
    is_vegan: bool = Field(False)
    is_spicy: bool = Field(False)
    image: Optional[str] = Field(None, description="Public image URL")
    featured: bool = Field(False, description="Show in highlights")

class Reservation(BaseModel):
    """
    Guest reservations
    Collection: "reservation"
    """
    name: str = Field(..., description="Guest full name")
    email: Optional[EmailStr] = Field(None, description="Guest email")
    phone: str = Field(..., description="Contact number")
    guests: int = Field(..., ge=1, le=20)
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field(..., description="HH:MM")
    notes: Optional[str] = Field(None, description="Special requests")

class Review(BaseModel):
    """
    Guest reviews
    Collection: "review"
    """
    name: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    source: Optional[str] = Field(None, description="e.g., Google, Yelp")
    avatar: Optional[str] = None

# Optional: basic marketing capture
class Newsletter(BaseModel):
    """
    Newsletter signups
    Collection: "newsletter"
    """
    email: EmailStr
    name: Optional[str] = None

# Timestamps are added automatically by database helpers
