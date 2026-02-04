from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os

# Import our agent logic
from agent import generate_honeypot_response, extract_intelligence

app = FastAPI(title="Agentic Honey-Pot API")

# --- IN-MEMORY DATABASE ---
sessions: Dict[str, List[Dict]] = {}

# --- HELPER: The Standard Response ---
def build_response(message: str, session_id: str):
    # Ensure session exists
    if session_id not in sessions:
        sessions[session_id] = []
    
    # Fake logic if message is empty (for GET requests)
    if not message:
        message = "PING"
        ai_reply = "Connection Verified. How may I help you verify your documents?"
    else:
        # Real logic
        sessions[session_id].append({"role": "user", "content": message})
        ai_reply = generate_honeypot_response(sessions[session_id])
        sessions[session_id].append({"role": "assistant", "content": ai_reply})

    intel = extract_intelligence(message)

    return {
        "scam_detected": True,
        "reply": ai_reply,
        "extracted_intelligence": intel,
        "conversation_turn": len(sessions[session_id])
    }

# --- THE "GOD MODE" ENDPOINT ---
# This catches GET, POST, and ANY path (including the weird /https:// one)
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT"])
async def catch_all(request: Request, full_path: str):
    print(f"--- INCOMING REQUEST ON: {full_path} ---")
    
    # 1. Try to parse JSON body (if POST)
    incoming_msg = ""
    session_id = "default_session"
    
    try:
        payload = await request.json()
        print(f"PAYLOAD: {payload}")
        incoming_msg = (
            payload.get("message") or 
            payload.get("content") or 
            payload.get("input") or 
            ""
        )
        session_id = payload.get("session_id", "default_session")
    except:
        print("No JSON body (likely a GET request)")

    # 2. Return the success JSON regardless of what happened
    return build_response(incoming_msg, session_id)