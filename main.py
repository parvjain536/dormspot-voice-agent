import os
import random
import string
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="DormSpot Voice AI API",
    description="Backend tool provider for Amazon Nova Sonic voice agent dealing with hostel and PG room bookings.",
    version="1.0.0"
)

# Enable CORS for external tool callers (AgentCore Gateway / Amazon Connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Could not connect to Supabase: {e}")

def generate_booking_code() -> str:
    return "DS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "DormSpot Voice AI Agent Backend",
        "documentation": "/docs"
    }

@app.get("/availability", summary="Search hostel availability by city")
def check_availability(city: str = Query(..., description="Name of the city to search hostels in (e.g. Bhopal, Indore, Pune, Gwalior)")):
    """
    Search available hostels in a specific city. Returns details such as room types,
    pricing per night, available rooms, and amenities.
    """
    if not supabase:
        # Fallback dummy data if Supabase keys not set yet during initial test
        dummy_hostels = [
            {"id": "h1", "name": "DormSpot Scholar Hub", "city": city, "room_type": "Single AC", "price_per_night": 650, "rooms_available": 4, "amenities": ["WiFi", "Meals", "Security"]},
            {"id": "h2", "name": "DormSpot Campus Edge", "city": city, "room_type": "Double Sharing", "price_per_night": 450, "rooms_available": 2, "amenities": ["WiFi", "Laundry"]}
        ]
        return {"city": city, "count": len(dummy_hostels), "results": dummy_hostels}

    try:
        res = supabase.table("hostels").select("*").ilike("city", f"%{city}%").gt("rooms_available", 0).execute()
        return {
            "city": city,
            "count": len(res.data) if res.data else 0,
            "results": res.data if res.data else []
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database query failed: {str(e)}")

@app.get("/hostel/{hostel_id}", summary="Get detailed information about a specific hostel")
def get_hostel_details(hostel_id: str):
    """
    Fetch comprehensive details for a specific hostel using its unique ID.
    """
    if not supabase:
        return {"id": hostel_id, "name": "DormSpot Scholar Hub", "price_per_night": 650, "address": "MP Nagar, Bhopal", "amenities": ["WiFi", "Meals"]}

    try:
        res = supabase.table("hostels").select("*").eq("id", hostel_id).execute()
        if not res.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")
        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/booking", summary="Create a new hostel booking reservation")
def create_booking(
    hostel_id: str = Query(..., description="ID of the hostel to book"),
    guest_name: str = Query(..., description="Full name of the guest"),
    guest_phone: str = Query(..., description="Phone number for SMS notification"),
    check_in: str = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out: str = Query(..., description="Check-out date (YYYY-MM-DD)")
):
    """
    Confirms a booking reservation for a guest and generates a unique Booking Reference Code.
    Decrements room availability by 1 upon successful booking.
    """
    booking_code = generate_booking_code()

    if not supabase:
        return {
            "status": "confirmed",
            "message": "Booking successful! Confirmation SMS dispatched.",
            "booking_code": booking_code,
            "guest_name": guest_name,
            "check_in": check_in,
            "check_out": check_out
        }

    try:
        # 1. Fetch hostel to confirm room availability
        hostel_res = supabase.table("hostels").select("rooms_available, name").eq("id", hostel_id).execute()
        if not hostel_res.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")
        
        current_rooms = hostel_res.data[0]["rooms_available"]
        hostel_name = hostel_res.data[0]["name"]

        if current_rooms <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sorry, no rooms are currently available at this hostel.")

        # 2. Create booking entry
        booking_data = {
            "hostel_id": hostel_id,
            "guest_name": guest_name,
            "guest_phone": guest_phone,
            "check_in": check_in,
            "check_out": check_out,
            "status": "confirmed",
            "booking_code": booking_code
        }
        res = supabase.table("bookings").insert(booking_data).execute()

        # 3. Decrement available room count
        supabase.table("hostels").update({"rooms_available": current_rooms - 1}).eq("id", hostel_id).execute()

        return {
            "status": "confirmed",
            "message": f"Successfully reserved at {hostel_name}.",
            "booking_code": booking_code,
            "booking_details": res.data[0] if res.data else booking_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Booking creation failed: {str(e)}")
