# DormSpot — AI Voice Self-Service Hostel Booking Agent
**Candidate Project Submission for DataSleek Hiring Assignment**

---

## 1. Executive Summary & Overview
**DormSpot** is a voice-first, self-service AI agent designed to assist students and young professionals in discovering, inquiring about, and instantly reserving hostel and co-living PG accommodations across multiple cities.

Powered by **Amazon Nova Sonic** (speech-to-speech foundation model on Amazon Bedrock) integrated with **Amazon Connect** and **AgentCore Gateway**, DormSpot seamlessly converts real-time voice conversations into precise, low-latency API tool calls against a live **FastAPI + Supabase PostgreSQL** backend.

---

## 2. Architecture & Data Flow Diagram

```
 Caller (Voice Call / Telephony / WebRTC)
                  │
                  ▼
       Amazon Connect (Voice Flow)
                  │
                  ▼
 Amazon Nova Sonic (Speech-to-Speech LLM via Bedrock)
                  │
                  ├─► MCP Tool Invocation (OpenAPI Schema)
                  │
                  ▼
      AWS AgentCore Gateway / MCP Gateway
                  │
                  ▼
       DormSpot FastAPI Backend (Render / Public HTTPS)
                  │
                  ▼
        Supabase PostgreSQL Database
  (Tables: `hostels` & `bookings`)
```

---

## 3. Key Tools & External API Integrations

DormSpot exposes three key tools via OpenAPI specification:

1. **`check_availability(city: str)`**:
   - **Purpose**: Queries live room counts, prices per night, amenities, and room types for a specified city (e.g. Bhopal, Indore, Pune, Gwalior).
   - **DB Table**: `hostels` where `rooms_available > 0`.

2. **`get_hostel_details(hostel_id: str)`**:
   - **Purpose**: Retrieves full property details including full address, security features, and meal plans.

3. **`create_booking(hostel_id, guest_name, guest_phone, check_in, check_out)`**:
   - **Purpose**: Reserves a room for the guest, generates a unique reference code (`DS-XXXXXX`), and automatically decrements room availability by 1 in real time.
   - **DB Table**: `bookings` (with foreign key reference to `hostels`).

---

## 4. Prompt Engineering & Voice Agent Design

- **Turn-Taking Optimizations**: Nova Sonic is tuned to deliver short, 1-3 sentence verbal responses optimized for natural conversational cadence over audio.
- **Graceful Error Handling**: If an invalid city is provided or the backend API experiences latency, the voice agent acknowledges the issue conversationally without hallucinating false availability or prices.
- **Data Integrity**: Strictly bound to tool responses; if a query returns 0 rooms, the agent suggests checking neighboring cities instead of fabricating inventory.

---

## 5. Architectural Trade-Offs & Future Enhancements

### Trade-Offs Made (Given Time Constraints):
- **Database Layer**: Used Supabase Free Tier (PostgreSQL) with seeded dummy data across 4 cities to showcase realistic multi-turn voice queries without incurring infrastructure costs.
- **Deployment**: Hosted FastAPI backend on Render / Vercel with CORS enabled for instant HTTPS accessibility by AgentCore Gateway.

### Future Improvements with More Time:
1. **Third-Party SMS/WhatsApp Notifications**: Wire Twilio / WhatsApp Business API into `create_booking` to dispatch real-time booking vouchers instantly during the voice call.
2. **Multi-Language Support**: Extend Nova Sonic prompts to support Hindi & regional Indian languages for diverse student demographics.
3. **Payment Gateway Integration**: Integrate Razorpay / UPI intent link generation over SMS for instant token deposit payment upon reservation.

---

## 6. How to Run & Verify

1. **Backend**:
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
2. **Interactive API Docs**: Visit `http://localhost:8000/docs` to test endpoints manually.
3. **Supabase Schema**: Execute `schema.sql` inside your Supabase SQL Editor.
