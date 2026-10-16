# FastAPI application
import asyncio
import secrets
import json
import redis
from fastapi import FastAPI, HTTPException, Response, status, Cookie
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


# Global contants
COUNT = 7


@app.post("/api/init_new_session")
def init_new_session(topic: str, difficulty: str, response: Response):
    '''
    This function runs only once when the user starts and new quiz session.
    It initalizes and stores the session state into redis server.
    '''
    if topic and difficulty:
        session_state = CreateSessionResponse(
            session_id=generate_session_id(),
            topic=topic,
            difficulty=difficulty
        )

        redis_service.hset(f"session:{session_state.session_id}:session-state", mapping={
            "topic": session_state.topic,
            "difficulty": session_state.difficulty,
            "score": session_state.score,
            "total_time_taken": session_state.total_time_taken,
            "average_time_taken": session_state.average_time_taken,
            "session_feedback": session_state.session_feedback
        })

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
async def generate_new_questions(session_id: str | None = Cookie(None), count: int = COUNT):
    '''
    This fuction is used to create new questions using the AI Service.
    It is asynchronous and generates new questions only
    when the total numer of available questions reaches
    minimum threshold of 2.
    '''
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        total_available_questions = redis_service.hlen("session:123:question_map")

        topic = redis_service.hget(f"session:{session_id}:session-state", "topic")
        difficulty = redis_service.hget(f"session:{session_id}:session-state", "difficulty")

        new_question_batch = await ai_service.generate_question_batch(
            topic=topic,
            difficulty=difficulty,
            count=count
        )

        i = 1
        for ques in new_question_batch.questions:
            ques.question_id = f"q{total_available_questions + i}"
            redis_service.hset(f"session:{session_id}:session-state", ques.question_id, ques.model_dump_json())
            i += 1

        return {"message": f"{count} new questions added successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not add new questions",
        )


@app.get("/api/get_question_by_id")
def get_question_by_id(question_id: str, session_id: str | None = Cookie(None)):
    pass
