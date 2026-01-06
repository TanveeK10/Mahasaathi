#!/usr/bin/env python3
"""
FastAPI wrapper for MahaSaathi chatbot
Provides REST API endpoints for Android app integration

Endpoints:
- POST /chat - Main chat endpoint
- GET /health - Health check endpoint
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# Add chatbot directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chatbot'))

from chatbot.chat_engine import chat_step
from chatbot.config import APP_NAME, DEBUG

# Initialize FastAPI app
app = FastAPI(
    title="MahaSaathi API",
    description="Pune Ganeshotsav Assistant API",
    version="1.0.0"
)

# Add CORS middleware for Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    user_uid: str
    query: str

class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str] = None
    debug: Optional[Dict[str, Any]] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service is running
    """
    return {
        "status": "healthy",
        "service": "MahaSaathi API",
        "version": "1.0.0"
    }

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for processing user queries
    
    Request body:
    {
        "user_uid": "string",  # User identifier (can be "anonymous")
        "query": "string"      # User's question
    }
    
    Response:
    {
        "reply": "string",     # Assistant's response
        "intent": "string",    # Detected intent (optional)
        "debug": {...}         # Debug information (optional, if DEBUG=True)
    }
    """
    try:
        # Validate input
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if not request.user_uid or not request.user_uid.strip():
            request.user_uid = "anonymous"
        
        # Process query through chat engine
        result = chat_step(request.user_uid, request.query, debug=False)
        
        # Build response
        response = ChatResponse(
            reply=result["reply"],
            intent=result["intent"],
            debug={
                "params": result.get("params"),
                "intent_data": result.get("intent_data"),
                "user_uid": request.user_uid
            } if DEBUG else None
        )
        
        return response
        
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "service": "MahaSaathi API",
        "version": "1.0.0",
        "description": "Pune Ganeshotsav Assistant API",
        "endpoints": {
            "POST /chat": "Main chat endpoint",
            "GET /health": "Health check",
            "GET /docs": "API documentation (Swagger UI)",
            "GET /redoc": "API documentation (ReDoc)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
