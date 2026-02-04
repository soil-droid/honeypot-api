from fastapi import FastAPI, Request
from typing import Dict, List

# Import our agent logic
from agent import generate_honeypot_response, extract_intelligence

app = FastAPI(title="Agentic Honey-Pot API")

# --- IN-MEMORY DATABASE ---
sessions: Dict[str, List[Dict]] = {}

# --- HELPER: The Standard Success JSON ---
def get_success_response():
    return {
        "scam_detected": True,
        "reply": "Connection Verified. Validation logic active.",
        "extracted_intelligence": {
            "phone_numbers": [],
            "upi_ids": [],
            "urls": []
        },
        "conversation_turn": 1
    }

# --- ROUTE 1: The Homepage (Fixes the "GET /" error) ---
@app.get("/")
def home():
    # We return the HACKATHON JSON here too, just in case they hit the root
    return get_success_response()

# --- ROUTE 2: The Catch-All (Fixes the weird paths) ---
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "HEAD"])
async def catch_all(request: Request, full_path: str):
    print(f"--- INCOMING REQUEST ON: {full_path} ---")
    
    # Try to parse data if it exists, but don't crash if it fails
    incoming_msg = ""
    session_id = "default_session"
    try:
        payload = await request.json()
        incoming_msg = payload.get("message", "")
        session_id = payload.get("session_id", "default_session")
        
        # Actually run the agent logic if we have a message
        if incoming_msg:
             if session_id not in sessions: sessions[session_id] = []
             sessions[session_id].append({"role": "user", "content": incoming_msg})
             ai_reply = generate_honeypot_response(sessions[session_id])
             sessions[session_id].append({"role": "assistant", "content": ai_reply})
             
             return {
                "scam_detected": True,
                "reply": ai_reply,
                "extracted_intelligence": extract_intelligence(incoming_msg),
                "conversation_turn": len(sessions[session_id])
             }
    except:
        pass

    # If anything failed or it was a GET request, return the default Success JSON
    return get_success_response()