# FastAPI application
import asyncio
import secrets
from fastapi import FastAPI, HTTPException, responses
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.schemas import *
from core.utilities import *
from core.services import AIService

app = FastAPI(title="AI Service API")

# Configure CORS so frontend can communicate with this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL/port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global contants
COUNT = 7
session_state = CreateSessionResponse(
    session_id="",
    topic="",
    difficulty=""
)

# Instantiate the service
ai_service = AIService()

# Question list
question_list = QuizBatch()


@app.post("/api/new_session")
def init_new_session(topic: str, difficulty: str):
    if topic and difficulty:
        session_state.session_id = generate_session_id()
        session_state.topic = topic
        session_state.difficulty = difficulty

        responses.set_cookie(
            key="session_id",
            value=session_state.session_id,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        return {"message": "session initialized successfully"}
    else:
        return {"error": "either topic or difficulty is missing"}



@app.post("/api/generate_new_questions")
async def add_questions(count: int = COUNT):
    try:
        new_question_batch = await ai_service.generate_question_batch(
            topic=session_state.topic,
            difficulty=session_state.difficulty,
            count=count
        )

        question_list.questions.extend(new_question_batch)
        return {"message": f"{count} new questions added successfully"}
    except:
        return {"error": "could not add new questions"}
