# 🎙️ DormSpot — Voice AI Hostel Booking Agent

A real-time, voice-driven AI assistant that finds and books hostel / PG rooms through natural spoken conversation — no typing, no forms. Built on **Amazon Nova Sonic** (real-time bidirectional speech AI) via **AWS Bedrock AgentCore**, with a custom **FastAPI + Supabase** backend.

**🔗 Live demo:** https://dz2rgtctzefud.cloudfront.net
**🔗 Backend API docs:** https://dormspot-voice-agent.onrender.com/docs

---

## What it does

A user opens the web app, signs in, and simply talks. The assistant:
- Greets them and asks which city they want to stay in
- Looks up real, live room availability and pricing
- Collects booking details by voice (name, phone, dates)
- Confirms a real booking with a unique reference code — stored in a live database

Every fact the assistant states comes from a real, live tool call — it never invents prices or availability (this is explicitly enforced in its system prompt).

---

## Architecture

| Layer | Technology |
|---|---|
| Frontend | React + Vite, hosted on S3 + CloudFront |
| Auth | Amazon Cognito (sign-up/login, temporary credentials) |
| Voice AI | Amazon Nova Sonic on Bedrock AgentCore Runtime |
| Agent framework | Python, FastAPI, Strands Agents (BidiAgent) |
| Backend API | FastAPI, deployed on Render |
| Database | Supabase (Postgres) |
| Infrastructure | AWS CDK (all AWS resources defined as code) |

User's browser (CloudFront + S3 — React frontend)
│ Login via Cognito
│ WebSocket connection
▼
AWS Bedrock AgentCore Runtime (Nova Sonic + Strands BidiAgent)
│ Tool calls when data is needed
▼
FastAPI backend (Render)
│
▼
Supabase (Postgres — hostels & bookings)

An Amazon Bedrock AgentCore **Gateway** was also configured, registering the backend's OpenAPI schema as a formal tool target — an alternative integration path alongside the direct HTTP calls used by the deployed agent.

---

## Repository Structure

dormspot-voice-agent/
├── backend/ # FastAPI + Supabase backend (deployed on Render)
│ ├── main.py # API endpoints: /availability, /hostel/{id}, /booking
│ ├── schema.sql # Supabase table definitions + seed data
│ ├── system_prompt.txt # Reference copy of the agent's system prompt
│ ├── requirements.txt
│ └── .env.example
│
├── voice-agent/ # Voice agent + frontend + AWS infrastructure
│ ├── agent/
│ │ └── strands_agent.py # BidiAgent: Nova Sonic, tools, system prompt
│ ├── frontend/ # React/Vite web app (mic capture, playback, chat UI)
│ ├── cdk/ # AWS CDK infrastructure (Runtime, Cognito, S3/CloudFront)
│ └── scripts/ # Deployment scripts (deploy-all, build-frontend)
│
└── README.md

This project was originally built on top of AWS's official sample, [`aws-samples/sample-nova-sonic-websocket-agentcore`](https://github.com/aws-samples/sample-nova-sonic-websocket-agentcore), which provided the base WebSocket/voice-streaming plumbing, CDK infrastructure, and deployment scripts. The DormSpot persona, tools, database, and backend API are custom work built on top of that foundation.

---

## Running It Yourself

### 1. Database (Supabase)
1. Create a free Supabase project.
2. Run `backend/schema.sql` in the SQL Editor to create the `hostels` and `bookings` tables.
3. Copy your Project URL and anon key from Project Settings → API.

### 2. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # then fill in SUPABASE_URL and SUPABASE_KEY
uvicorn main:app --reload
```
Visit `http://localhost:8000/docs` to test the API directly.

### 3. Voice Agent + Frontend (AWS)
Requires an AWS account and the AWS CLI configured.
```bash
cd voice-agent
./deploy-all.ps1        # PowerShell 7 (pwsh) recommended
```
This deploys the Cognito auth, Bedrock AgentCore runtime, and the S3/CloudFront-hosted frontend. See `voice-agent/scripts/` for individual build/deploy steps.

---

## How the Agent's Behavior Is Defined

Nova Sonic is a general-purpose, pretrained voice model — nothing here was fine-tuned or trained. Its DormSpot behavior comes entirely from a system prompt and a small set of tools:

check_availability(city) → searches real listings by city
get_hostel_details(hostel_id) → fetches one listing's full details
create_booking(...) → creates a real booking, decrements availability

The system prompt explicitly instructs the model to only state facts returned by these tools, and never to invent pricing or availability.

---

## Known Limitations

- The Render backend runs on a free tier, which sleeps after inactivity — the first request after idle time can take 30–60+ seconds.
- Row Level Security (RLS) is currently disabled on the Supabase tables; for production use this should be enabled with appropriate policies.
- Conversation memory is session-scoped only — a new agent session starts fresh with no memory of prior conversations.

---

## Tech Stack

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![AWS Bedrock](https://img.shields.io/badge/AWS%20Bedrock-FF9900?style=for-the-badge&logo=amazonaws) ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase) ![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react)