import os
import uuid
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory session storage
# Format: {session_id: [{"role": "...", "content": "..."}]}
sessions: Dict[str, List[Dict[str, str]]] = {}

SYSTEM_PROMPT = """You are a knowledgeable assistant focused on Berlin's conscious and sober scene.
You help people discover and navigate the sober-curious lifestyle in Berlin, including:
- Alcohol-free events, parties, and social gatherings
- Sober-friendly venues, cafes, and clubs
- Wellness activities like yoga, meditation, breathwork
- Conscious community events and meetups
- Mental health and personal growth resources
- Non-alcoholic drink recommendations

Keep responses friendly, supportive, and focused on Berlin's vibrant sober community.
Only discuss topics related to Berlin's conscious/sober scene."""


class SessionResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str


@app.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a new chat session and return session ID"""
    session_id = str(uuid.uuid4())

    # Initialize session with system prompt
    sessions[session_id] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    return SessionResponse(session_id=session_id)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # If session_id provided, use session history
        if request.session_id:
            if request.session_id not in sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            # Get conversation history
            messages = sessions[request.session_id]

            # Add user message to history
            messages.append({"role": "user", "content": request.message})
        else:
            # No session: single-turn conversation (backward compatibility)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ]

        # Call OpenAI with full history
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content

        # If using session, store assistant response in history
        if request.session_id:
            sessions[request.session_id].append(
                {"role": "assistant", "content": assistant_message}
            )

        return ChatResponse(response=assistant_message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
