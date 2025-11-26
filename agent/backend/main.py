import os
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


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content
        return ChatResponse(response=assistant_message)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
