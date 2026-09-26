# FastAPI application
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.schemas import *
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
TOPIC = ""
DIFFICULTY = ""
COUNT = 5

# Instantiate the service
ai_service = AIService()

# Question list
question_list = QuizBatch()


@app.post("/api/new_session")
def init_new_session(topic: str, difficulty: str):
    global TOPIC
    global DIFFICULTY

    if topic and difficulty:
        TOPIC = topic
        DIFFICULTY = difficulty
        return {"message": "session initialized successfully"}
    else:
        return {"error": "either topic or difficulty is missing"}



@app.post("/api/generate_new_questions")
async def add_questions(count: int = COUNT):
    try:
        new_question_batch = await ai_service.generate_question_batch(
            topic=TOPIC,
            difficulty=DIFFICULTY,
            count=count
        )

        question_list.questions.extend(new_question_batch)
        return {"message": f"{count} new questions added successfully"}
    except:
        return {"error": "could not add new questions"}
