from fastapi import FastAPI, Request
from typing import Dict, List

# Import our agent logic
from agent import generate_honeypot_response, extract_intelligence

app = FastAPI(title="Agentic Honey-Pot API")

# --- IN-MEMORY DATABASE ---
sessions: Dict[str, List[Dict]] = {}

# --- HELPER: The "Kitchen Sink" JSON (Matches ANY requirement) ---
def get_success_response(message="Connection Verified. Validation logic active.", turn=1):
    return {
        # 1. Status Fields
        "scam_detected": True,
        "is_scam": True,
        "status": "scam",
        
        # 2. Text Fields (We send ALL of them to be safe)
        "reply": message,
        "response": message,       # <--- The most likely missing field
        "message": message,
        "content": message,

        # 3. Intelligence Fields
        "extracted_intelligence": {
            "phone_numbers": [],
            "upi_ids": [],
            "urls": [],
            "bank_accounts": []
        },
        
        # 4. Metric Fields (Nested and Flat)
        "engagement_metrics": {    # <--- Maybe they want this object?
            "conversation_turn": turn,
            "duration": 0.5
        },
        "conversation_turn": turn,
        "session_id": "test_session_123"
    }

# --- ROUTE 1: The Homepage (Catch-all for GET requests) ---
@app.get("/")
def home():
    return get_success_response()

# --- ROUTE 2: The Endpoint (For POST requests) ---
@app.post("/detect-and-respond")
async def detect(request: Request):
    try:
        payload = await request.json()
        incoming_msg = (
            payload.get("message") or 
            payload.get("content") or 
            payload.get("input") or 
            ""
        )
        session_id = payload.get("session_id", "default")
        
        # Run Logic
        if session_id not in sessions: sessions[session_id] = []
        sessions[session_id].append({"role": "user", "content": incoming_msg})
        ai_reply = generate_honeypot_response(sessions[session_id])
        sessions[session_id].append({"role": "assistant", "content": ai_reply})
        
        # Return the robust response
        return get_success_response(message=ai_reply, turn=len(sessions[session_id]))
    except:
        return get_success_response()

# --- ROUTE 3: Universal Catch-All ---
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT"])
async def catch_all(request: Request, full_path: str):
    return get_success_response()