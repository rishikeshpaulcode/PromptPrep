import json
import logging

import redis
from fastapi import (
    BackgroundTasks,
    Cookie,
    FastAPI,
    HTTPException,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware

from core.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    LLMSessionFeedback,
    LLMWeakConcept,
    QuestionPublic,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from core.services import AIService
from core.utilities import generate_session_id


logging.basicConfig(level=logging.INFO)

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
redis_service = redis.Redis(host="localhost", port=6379, decode_responses=True)

try:
    if redis_service.ping():
        logging.getLogger(__name__).info("Connected to Redis successfully!")
except redis.ConnectionError:
    logging.getLogger(__name__).error("Could not connect to Redis server.")


# Instantiate the service
ai_service = AIService()


# Global contants
COUNT = 7
MIN_QUES_THRESHOLD = 3
CORRECT_ANSWER_POINTS = 4
INCORRECT_ANSWER_POINTS = -1


def generate_new_questions(session_id: str, count: int = COUNT) -> None:
    """
    Create new questions using the AI service when the question pool is low.
    """
    redis_service.hset(
        f"session:{session_id}:session-state",
        "is_generating_question_batch",
        True,
    )

    total_available_questions = redis_service.hlen(
        f"session:{session_id}:question-map"
    )
    topic = redis_service.hget(f"session:{session_id}:session-state", "topic")
    difficulty = redis_service.hget(
        f"session:{session_id}:session-state", "difficulty"
    )

    new_question_batch = ai_service.generate_question_batch(
        topic=topic,
        difficulty=difficulty,
        count=count,
    )

    i = 1
    for ques in new_question_batch.questions:
        ques.question_id = f"q{total_available_questions + i}"
        redis_service.hset(
            f"session:{session_id}:question-map",
            ques.question_id,
            ques.model_dump_json(),
        )
        i += 1

    redis_service.hset(
        f"session:{session_id}:session-state",
        "is_generating_question_batch",
        False,
    )


@app.post("/api/init_new_session", status_code=status.HTTP_201_CREATED)
def init_new_session(
    payload: CreateSessionRequest, response: Response
) -> dict[str, str]:
    """
    Initialize a new quiz session and store its state in Redis.
    """
    session_id = generate_session_id()

    session_state = CreateSessionResponse(
        topic=payload.topic,
        difficulty=payload.difficulty,
    )

    redis_service.hset(
        f"session:{session_id}:session-state",
        mapping=session_state.model_dump(),
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Session initialized successfully"}


@app.post("/api/init_new_quiz", status_code=status.HTTP_201_CREATED)
def init_new_quiz(
    count: int = COUNT, session_id: str | None = Cookie(None)
) -> dict[str, str]:
    """Generate the initial question batch for the current session."""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    generate_new_questions(session_id=session_id, count=count)
    num_generated_questions = redis_service.hlen(f"session:{session_id}:question-map")

    if num_generated_questions == count:
        return {"message": f"Inintial {count} questions generated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Background question generation failed",
        )


@app.get("/api/get_next_question", response_model=QuestionPublic)
def get_next_question(
    background_tasks: BackgroundTasks, session_id: str | None = Cookie(None)
) -> QuestionPublic:
    """
    Retrieve the next question and replenish the pool when it reaches its threshold.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    num_generated_questions = redis_service.hlen(f"session:{session_id}:question-map")
    n = (
        redis_service.hget(
            f"session:{session_id}:session-state", "num_questions_delivered"
        )
        + 1
    )
    next_question_id = f"q{n}"

    raw_data = redis_service.hget(
        f"session:{session_id}:question-map", next_question_id
    )
    if not raw_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    question_detials = json.loads(raw_data)
    question_secure = QuestionPublic(
        question_id=question_detials["question_id"],
        question_text=question_detials["question_text"],
        options=question_detials["options"],
    )

    num_fresh_questions = num_generated_questions - n
    is_generating = redis_service.hget(
        f"session:{session_id}:session-state", "is_generating_question_batch"
    )
    if not is_generating and num_fresh_questions <= MIN_QUES_THRESHOLD:
        background_tasks.add_task(generate_new_questions, session_id=session_id)

    redis_service.hset(
        f"session:{session_id}:session-state", "num_questions_delivered", n
    )
    return question_secure


@app.post("/api/check_answer", response_model=SubmitAnswerResponse)
def check_answer(
    payload: SubmitAnswerRequest, session_id: str | None = Cookie(None)
) -> SubmitAnswerResponse:
    """
    Evaluate an answer and update the session score and counters in Redis.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_state = redis_service.hgetall(f"session:{session_id}:session-state")
    if not session_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session details not found",
        )

    raw_data = redis_service.hget(f"session:{session_id}:question-map", payload.question_id)
    if not raw_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    question_details = json.loads(raw_data)
    curr_score = int(session_state["score"])
    curr_num_questions_correct = int(session_state["num_questions_correct"])
    curr_num_questions_incorrect = int(session_state["num_questions_incorrect"])

    is_correct = (
        payload.selected_option_index == question_details["correct_option_index"]
    )

    evaluation_response = SubmitAnswerResponse(
        question_id=payload.question_id,
        is_correct=is_correct,
        correct_option_index=question_details["correct_option_index"],
        explanation=question_details["explanation"],
    )

    if evaluation_response.is_correct:
        new_score = curr_score + CORRECT_ANSWER_POINTS
        new_num_questions_correct = curr_num_questions_correct + 1
        new_num_questions_incorrect = curr_num_questions_incorrect
    else:
        new_score = curr_score + INCORRECT_ANSWER_POINTS
        new_num_questions_correct = curr_num_questions_correct
        new_num_questions_incorrect =  curr_num_questions_incorrect + 1
        redis_service.rpush(
            f"session:{session_id}:incorrect-questions",
            question_details["question_text"],
        )

    redis_service.hset(
        f"session:{session_id}:session-state",
        mapping={
            "score": new_score,
            "num_questions_correct": new_num_questions_correct,
            "num_questions_incorrect": new_num_questions_incorrect,
        },
    )

    return evaluation_response


@app.get("/api/get_session_feedback", response_model=LLMSessionFeedback)
def get_session_feedback(
    session_id: str | None = Cookie(None),
) -> LLMSessionFeedback:
    """
    Return AI-generated feedback for concepts missed in the current session.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_state = redis_service.hgetall(f"session:{session_id}:session-state")
    if not session_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session details not found",
        )

    incorrect_question_texts = redis_service.lrange(
        f"session:{session_id}:incorrect-questions", 0, -1
    )
    if not incorrect_question_texts:
        return LLMSessionFeedback(
            weak_concepts=[
                LLMWeakConcept(
                    concept="No weak concepts identified",
                    advice="Good job! Keep it up.",
                )
            ]
        )

    return ai_service.get_session_feedback(
        topic=session_state["topic"],
        incorrect_question_texts=incorrect_question_texts,
    )


@app.get("/api/get_session_summary", response_model=CreateSessionResponse)
def get_session_summary(
    session_id: str | None = Cookie(None),
) -> CreateSessionResponse:
    """
    Return the session state and overall results when a quiz session ends.
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_state = redis_service.hgetall(f"session:{session_id}:session-state")
    if not session_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session details not found",
        )

    return session_state

