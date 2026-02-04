from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import uuid

# Import our agent logic
from agent import generate_honeypot_response, extract_intelligence

app = FastAPI(title="Agentic Honey-Pot API")

# --- IN-MEMORY DATABASE ---
sessions: Dict[str, List[Dict]] = {}

# --- FLEXIBLE ENDPOINT ---
@app.post("/detect-and-respond")
async def chat_endpoint(request: Request):
    """
    Accepts ANY JSON payload to debug field names.
    """
    try:
        # 1. Get the raw JSON
        payload = await request.json()
        print(f"--- DEBUG: INCOMING PAYLOAD ---\n{payload}\n-------------------------------")

        # 2. Dynamically find the message and session_id
        # We check multiple common variations of field names
        incoming_msg = (
            payload.get("message") or 
            payload.get("text") or 
            payload.get("content") or 
            payload.get("input") or 
            ""
        )
        
        session_id = (
            payload.get("session_id") or 
            payload.get("id") or 
            payload.get("conversation_id") or 
            "default_session"
        )

        # 3. If empty, return a safe error (so the platform doesn't crash)
        if not incoming_msg:
            return {
                "error": "No message field found",
                "received_keys": list(payload.keys())
            }

        # 4. Standard Logic
        if session_id not in sessions:
            sessions[session_id] = []
        
        sessions[session_id].append({"role": "user", "content": incoming_msg})
        ai_reply = generate_honeypot_response(sessions[session_id])
        sessions[session_id].append({"role": "assistant", "content": ai_reply})
        intel = extract_intelligence(incoming_msg)

        # 5. Return the Standard Response
        return {
            "scam_detected": True,
            "reply": ai_reply,
            "extracted_intelligence": intel,
            "conversation_turn": len(sessions[session_id])
        }

    except Exception as e:
        print(f"ERROR PROCESSING REQUEST: {e}")
        return {"error": str(e)}

@app.get("/")
def home():
    return {"status": "Online"}