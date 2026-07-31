import os
import requests
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from strands.experimental.bidi import BidiAgent
from strands.experimental.bidi.models import BidiNovaSonicModel
from strands.experimental.bidi.tools import stop_conversation
from strands import tool

# Environment configuration
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-2-sonic-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")
# BEDROCK_REGION controls where Nova Sonic model calls are made.
# Defaults to us-east-1. Nova Sonic is only available in select regions.
# See: https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
INPUT_SAMPLE_RATE = int(os.getenv("INPUT_SAMPLE_RATE", "16000"))
OUTPUT_SAMPLE_RATE = int(os.getenv("OUTPUT_SAMPLE_RATE", "16000"))
CHANNELS = int(os.getenv("CHANNELS", "1"))
FORMAT = os.getenv("FORMAT", "pcm")

# DormSpot API base URL (your deployed Render app)
DORMSPOT_API = os.getenv("DORMSPOT_API", "https://dormspot-voice-agent.onrender.com")

# Create FastAPI app
app = FastAPI()

# ---- DormSpot tools ----

@tool
def check_availability(city: str) -> str:
    """
    Search available hostels in a specific city. Returns details such as
    room types, pricing per night, available rooms, and amenities.

    Args:
        city: Name of the city to search hostels in (e.g. Bhopal, Indore, Pune, Gwalior)

    Returns:
        Available hostels with pricing and room info
    """
    try:
        response = requests.get(f"{DORMSPOT_API}/availability", params={"city": city}, timeout=10)
        return str(response.json())
    except Exception as e:
        return f"Sorry, I'm having trouble accessing live availability right now: {str(e)}"


@tool
def get_hostel_details(hostel_id: str) -> str:
    """
    Fetch comprehensive details for a specific hostel using its unique ID.

    Args:
        hostel_id: The unique ID of the hostel

    Returns:
        Detailed hostel info
    """
    try:
        response = requests.get(f"{DORMSPOT_API}/hostel/{hostel_id}", timeout=10)
        return str(response.json())
    except Exception as e:
        return f"Sorry, I couldn't fetch that hostel's details: {str(e)}"


@tool
def create_booking(hostel_id: str, guest_name: str, guest_phone: str, check_in: str, check_out: str) -> str:
    """
    Confirms a booking reservation for a guest and generates a unique
    Booking Reference Code. Decrements room availability by 1 upon
    successful booking.

    Args:
        hostel_id: ID of the hostel to book
        guest_name: Full name of the guest
        guest_phone: Phone number for SMS notification
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)

    Returns:
        Booking confirmation
    """
    try:
        response = requests.post(
            f"{DORMSPOT_API}/booking",
            params={
                "hostel_id": hostel_id,
                "guest_name": guest_name,
                "guest_phone": guest_phone,
                "check_in": check_in,
                "check_out": check_out,
            },
            timeout=45,
        )
        return str(response.json())
    except Exception as e:
        return f"Sorry, the booking couldn't be completed: {str(e)}"


# Configure Nova Sonic model
sonic_model = BidiNovaSonicModel(
    model_id=MODEL_ID,
    provider_config={
        "audio": {
            "voice": "tiffany",  # Options: "tiffany" or "matthew"
            "input_rate": INPUT_SAMPLE_RATE,
            "output_rate": OUTPUT_SAMPLE_RATE,
            "channels": CHANNELS,
            "format": FORMAT
        },
        # Additional inference parameters can be added here
        # https://docs.aws.amazon.com/nova/latest/userguide/input-events.html
        "inference": {}
    },
    client_config={
        "region": BEDROCK_REGION
    },
)

# Health check endpoint (required by AgentCore)
@app.get("/ping")
async def ping():
    """Health check endpoint for AgentCore Runtime"""
    return {"status": "Healthy", "time_of_last_update": int(datetime.now().timestamp())}

# WebSocket endpoint for bidirectional voice chat
@app.websocket("/ws")
async def voice_chat(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for bidirectional voice streaming.

    This endpoint:
    1. Accepts WebSocket connections
    2. Creates a BidiAgent with Nova Sonic model
    3. Streams audio/text input from client
    4. Streams audio/text output back to client
    5. Supports tool execution (DormSpot hostel booking tools)
    6. Handles interruptions (barge-in)
    """
    # Create a new agent instance for this connection
    voice_agent = BidiAgent(
        model=sonic_model,
        tools=[check_availability, get_hostel_details, create_booking, stop_conversation],
        system_prompt=(
            "You are DormSpot, a voice assistant helping travelers find and book hostel "
            "or PG rooms. Greet the caller warmly. Ask which city they want to stay in. "
            "Use check_availability to find real options and read out 2-3 top results "
            "with price. If they want to book, collect their name, phone number, "
            "check-in and check-out dates, then use create_booking. If no rooms are "
            "available, apologize and offer to check a nearby city. Never make up "
            "availability or prices — only use real tool results."
        )
    )

    try:
        # Accept the WebSocket connection
        await websocket.accept()
        print("WebSocket connection accepted")

        # Run the bidirectional agent
        # Strands provides direct WebSocket integration!
        # - websocket.receive_json reads input events from client
        # - websocket.send_json sends output events to client
        await voice_agent.run(
            inputs=[websocket.receive_json],
            outputs=[websocket.send_json]
        )

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in voice chat: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await websocket.close()
            await voice_agent.stop()
        except Exception as cleanup_error:
            # Log cleanup errors but don't raise to avoid masking original exception
            print(f"Error during cleanup: {cleanup_error}")

# For local development/testing
if __name__ == "__main__":
    import uvicorn
    print(f"Starting voice agent server on port 8080...")
    print(f"Model: {MODEL_ID}")
    print(f"Region: {REGION}")
    print(f"Bedrock Region: {BEDROCK_REGION}")
    print(f"Audio config: {INPUT_SAMPLE_RATE}Hz, {CHANNELS} channel(s), {FORMAT} format")

    # Use localhost for local development, 0.0.0.0 only in containerized environments
    host = "0.0.0.0" if os.getenv("CONTAINER_ENV") else "127.0.0.1"
    print(f"Binding to: {host}")
    uvicorn.run(app, host=host, port=8080)