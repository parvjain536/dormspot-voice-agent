# 🎙️ DormSpot — AI Voice Self-Service Agent for Hostel Bookings

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![AWS Bedrock Nova Sonic](https://img.shields.io/badge/AWS-Amazon%20Nova%20Sonic-FF9900?style=for-the-badge&logo=amazonaws)](https://aws.amazon.com/bedrock/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)

An original Voice AI solution built for the **DataSleek Hiring Assignment**. Powered by **Amazon Nova Sonic (Speech-to-Speech)** on Bedrock, **Amazon Connect**, **AgentCore Gateway (MCP)**, and a **FastAPI + Supabase** backend.

---

## 📁 Repository Structure

```
dormspot-voice-agent/
├── main.py              # FastAPI application & tool endpoints
├── schema.sql           # Supabase SQL database schema & seed data
├── system_prompt.txt    # Nova Sonic voice agent system prompt & turn rules
├── writeup.md           # Submission write-up (Architecture, Trade-offs, Future Scope)
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

---

## ⚡ Quick Start Setup

### 1. Database Setup (Supabase)
1. Go to [Supabase](https://supabase.com) (Free Tier) and create a new project named `dormspot-db`.
2. Open the **SQL Editor** in Supabase and paste the contents of `schema.sql`.
3. Click **Run** to generate the `hostels` and `bookings` tables and seed dummy data for Bhopal, Indore, Pune, and Gwalior.
4. Copy your `Project URL` and `anon public key` from **Project Settings -> API**.

### 2. Backend API Setup (Local)
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/dormspot-voice-agent.git
   cd dormspot-voice-agent
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Add your `SUPABASE_URL` and `SUPABASE_KEY` inside `.env`.

5. Run the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```
6. Open your browser to `http://localhost:8000/docs` to test the live API endpoints!

---

## 🚀 Public Deployment (Free)

Deploy the FastAPI backend to [Render](https://render.com) or [Vercel](https://vercel.com) so that **AWS AgentCore Gateway** can reach your live API:

1. Push your code to GitHub.
2. Connect your repo to Render (New Web Service -> Python environment).
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Add `SUPABASE_URL` and `SUPABASE_KEY` in Environment Variables.
6. Copy your deployed HTTPS URL (e.g., `https://dormspot-api.onrender.com`).

---

## 🎙️ AWS Bedrock & Amazon Connect Setup

1. In AWS Console (`us-east-1`), request access to **Amazon Nova Sonic** under Bedrock Model Access.
2. Follow the AWS Workshop instructions to register your deployed API's OpenAPI spec (`https://dormspot-api.onrender.com/openapi.json`) into **AgentCore Gateway**.
3. Set the System Prompt from `system_prompt.txt` inside your Amazon Connect Voice Flow configuration.
4. Call your Amazon Connect phone number or use the WebRTC agent workspace to test the live voice conversation!
