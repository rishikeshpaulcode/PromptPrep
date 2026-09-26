# contains the schemas that are to be used to validate llm responces and store in redis db

from typing import List
from pydantic import BaseModel, Field


class QuestionInternal(BaseModel):
    """
    Internal question details.
    Contains all question details including answer key and explaination.
    """
    id: int
    question_text: str = Field(description="The quiz question text")
    options: List[str] = Field(description="List of exactly 4 choices")
    correct_option_index: int = Field(description="Index (0-3) of correct answer")
    explanation: str = Field(description="Why the answer is correct")


class QuestionPublic(BaseModel):
    """
    Public-facing question representation safe to send to the client UI.
    Excludes answer keys and explanations.
    """
    id: int
    question_text: str
    options: List[str]


class QuizBatch(BaseModel):
    """
    Structured payload schema passed to LangChain to force the LLM 
    to generate multiple questions in a single response.
    """
    questions: List[QuestionInternal] = Field(default=[])


class CreateSessionRequest(BaseModel):
    """
    Structured payload schema passed to LangChain to force the LLM 
    to generate multiple questions in a single JSON response.
    """
    topic: str
    difficulty: str


class CreateSessionResponse(BaseModel):
    """
    Response returned upon successfully initializing a quiz session.
    Provides immediate payload to bootstrap the client feed.
    """
    session_id: str
    initial_questions: List[QuestionPublic]


class SubmitAnswerRequest(BaseModel):
    """
    Payload sent by the client when submitting an answer for evaluation.
    """
    question_id: int
    selected_option_index: int


class SubmitAnswerResponse(BaseModel):
    """
    Response returned after evaluating a submitted answer.
    """
    question_id: int
    is_correct: bool
    correct_option_index: int
    explanation: str
