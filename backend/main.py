# FastAPI application
import asyncio
import secrets
import redis
from fastapi import FastAPI, HTTPException, Response, status
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

# Instantiate Redis server
redis_service = redis.Redis(host='localhost', port=6379, decode_responses=True)

try:
    if redis_service.ping():
        print("Connected to Redis successfully!")
except redis.ConnectionError:
    print("Could not connect to Redis server.")


# Instantiate the service
ai_service = AIService()


# global contants
COUNT = 7
session_state = CreateSessionResponse(
    session_id="",
    topic="",
    difficulty=""
)


# Question list
question_list = QuizBatch()


@app.post("/api/new_session")
def init_new_session(topic: str, difficulty: str, response: Response):
    if topic and difficulty:
        session_state.session_id = generate_session_id()
        session_state.topic = topic
        session_state.difficulty = difficulty

        response.set_cookie(
            key="session_id",
            value=session_state.session_id,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        return {"message": "Session initialized successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Either topic or difficulty is missing"
        )



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
