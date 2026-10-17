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
CORRECT_ANSWER_POINTS = 4
INCORRECT_ANSWER_POINTS = -1


@app.post("/api/init_new_session", status_code=status.HTTP_201_CREATED)
def init_new_session(payload: CreateSessionRequest, response: Response):
    """
    This function runs only once when the user starts and new quiz session.
    It initalizes and stores the session state into redis server.
    """
    session_id=generate_session_id()

    session_state = CreateSessionResponse(
        topic=payload.topic,
        difficulty=payload.difficulty
    )

    redis_service.hset(f"session:{session_id}:session-state", mapping=session_state.model_dump())

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return {"message": "Session initialized successfully"}


@app.post("/api/generate_new_questions", status_code=status.HTTP_201_CREATED)
async def generate_new_questions(count: int = COUNT, session_id: str | None = Cookie(None)):
    """
    This fuction is used to create new questions using the AI Service.
    It is asynchronous and generates new questions only
    when the total numer of available questions reaches
    minimum threshold of 2.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        total_available_questions = redis_service.hlen(f"session:{session_id}:question_map")
        # extra_questions_available =  hget(f"session:{session_id}:session-state", "num_questions_delivered")

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
            redis_service.hset(f"session:{session_id}:question_map", ques.question_id, ques.model_dump_json())
            i += 1

        return {"message": f"{count} new questions added successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not add new questions",
        )


@app.get("/api/get_next_question")
def get_next_question(session_id: str | None = Cookie(None)):
    """
    Retrieves a specific question by its unique identifier.
    Args:
        question_id: The unique ID of the question to fetch.
        session_id: Optional session tracking cookie.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    n = redis_service.hget(f"session:{session_id}:session-state", "num_questions_delivered")
    next_question_id = f"q{n + 1}"

    raw_data = redis_service.hget(f"session:{session_id}:question_map", next_question_id)
    if not raw_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    question_detials = json.loads(raw_data)
    question_secure = QuestionPublic(
        question_id=question_detials["question_id"],
        question_text=question_detials["question_text"],
        options=question_detials["options"]
    )

    redis_service.hset(f"session:{session_id}:session-state", "num_questions_delivered", n + 1)
    return question_secure


@app.post("/api/check_answer")
def check_answer(payload: SubmitAnswerRequest, session_id: str | None = Cookie(None)):
    """
    Evaluates a user's answer submission,
    Updates session scores and counters in Redis,
    and returns the correctness evaluation.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_state = redis_service.hgetall(f"session:{session_id}:session-state")
    if not session_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session details not found")

    raw_data = redis_service.hget(f"session:{session_id}:question_map", payload.question_id)
    if not raw_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    
    question_details = json.loads(raw_data)
    curr_score = int(session_state["score"])
    curr_num_questions_correct = int(session_state["num_questions_correct"])
    curr_num_questions_incorrect = int(session_state["num_questions_incorrect"])

    is_correct = (payload.selected_option_index == question_details["correct_option_index"])

    evaluation_response = SubmitAnswerResponse(
        question_id=payload.question_id,
        is_correct=is_correct,
        correct_option_index=question_details["correct_option_index"],
        explanation=question_details["explanation"]
    )

    if evaluation_response.is_correct:
        new_score = curr_score + CORRECT_ANSWER_POINTS
        new_num_questions_correct = curr_num_questions_correct + 1
        new_num_questions_incorrect = curr_num_questions_incorrect
    else:
        new_score =  curr_score + INCORRECT_ANSWER_POINTS
        new_num_questions_correct = curr_num_questions_correct
        new_num_questions_incorrect =  curr_num_questions_incorrect + 1

    redis_service.hset(f"session:{session_id}:session-state", mapping={
        "score": new_score,
        "num_questions_correct": new_num_questions_correct,
        "num_questions_incorrect": new_num_questions_incorrect
    })

    return evaluation_response

