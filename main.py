from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import uuid

# Import our agent logic
from agent import generate_honeypot_response, extract_intelligence

app = FastAPI(title="Agentic Honey-Pot API")

# --- IN-MEMORY DATABASE (For the Hackathon) ---
# In production, use Redis. For a hackathon, a Dict is fine.
# Structure: { "session_id": [ {role: "user", content: "..."} ] }
sessions: Dict[str, List[Dict]] = {}

# --- INPUT MODELS ---
# Adjust these field names based on the OFFICIAL Hackathon Docs
class ScamMessage(BaseModel):
    session_id: str = Field(..., description="Unique ID for this conversation")
    message: str = Field(..., description="The message from the scammer")
    metadata: Optional[dict] = None

class IntelligenceResponse(BaseModel):
    scam_detected: bool
    reply: str
    extracted_intelligence: dict
    conversation_turn: int

# --- THE ENDPOINT ---
@app.post("/detect-and-respond", response_model=IntelligenceResponse)
async def chat_endpoint(payload: ScamMessage, x_api_key: str = Header(None)):
    """
    Receives a scam message, processes it via the Honey-Pot Agent, and returns a reply.
    """
    # 1. Authenticate (Optional security for the hackathon)
    # if x_api_key != "YOUR_SECRET_KEY":
    #     raise HTTPException(status_code=401, detail="Invalid API Key")

    session_id = payload.session_id
    incoming_msg = payload.message

    # 2. Initialize session if new
    if session_id not in sessions:
        sessions[session_id] = []
    
    # 3. Add User message to memory
    sessions[session_id].append({"role": "user", "content": incoming_msg})

    # 4. Generate AI Response (The "Vikram" Persona)
    ai_reply = generate_honeypot_response(sessions[session_id])
    
    # 5. Add AI message to memory
    sessions[session_id].append({"role": "assistant", "content": ai_reply})

    # 6. Extract Intelligence (Did they reveal a bank account?)
    # We scan the *incoming* message for scammer details
    intel = extract_intelligence(incoming_msg)

    # 7. Return the structured JSON
    return {
        "scam_detected": True, # In a real app, you'd use a classifier here. For Honey-Pot, assume True.
        "reply": ai_reply,
        "extracted_intelligence": intel,
        "conversation_turn": len(sessions[session_id])
    }

# --- HEALTH CHECK ---
@app.get("/")
def home():
    return {"status": "Agent Vikram is Online and Ready to Waste Time."}