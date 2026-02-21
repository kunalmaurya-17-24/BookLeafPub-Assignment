import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent import run_customer_bot

app = FastAPI(title="BookLeaf Publishing AI Automation API")

class ChatRequest(BaseModel):
    query: str
    platform: str = "web" # 'whatsapp', 'instagram', 'email', 'web'
    sender_id: str # Handle or phone number

class ChatResponse(BaseModel):
    response: str
    platform: str
    sender_id: str
    verified_email: Optional[str]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint for the multi-channel customer bot.
    Handles identity resolution and agent workflow.
    """
    try:
        # Run the agent workflow
        bot_response = run_customer_bot(
            user_input=request.query,
            platform=request.platform,
            sender_id=request.sender_id
        )
        
        return ChatResponse(
            response=bot_response,
            platform=request.platform,
            sender_id=request.sender_id,
            verified_email=None # We could return this if needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "online", "service": "BookLeaf AI Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
