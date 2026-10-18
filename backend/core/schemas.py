# contains the schemas that are to be used to validate llm responces and store in redis db

from typing import List
from pydantic import BaseModel, Field


class LLMQuestionDetails(BaseModel):
    """
    Contains all question details including answer key and explaination.
    To be used to guide LLM to generate question it this order.
    """
    question_id: str = Field(description="Leave this field empty if you are AI")
    question_text: str = Field(description="The quiz question text")
    options: List[str] = Field(description="List of exactly 4 choices")
    correct_option_index: int = Field(description="Index (0-3) of correct answer")
    explanation: str = Field(description="Why the answer is correct")


class LLMQuizBatch(BaseModel):
    """
    Structured payload schema passed to LangChain to force the LLM 
    to generate multiple questions in a single response.
    """
    questions: List[LLMQuestionDetails]


class QuestionPublic(BaseModel):
    """
    Public-facing question representation safe to send to the client UI.
    Excludes answer keys and explanations.
    """
    question_id: str
    question_text: str
    options: List[str]


class CreateSessionRequest(BaseModel):
    """
    Structure of request to be sent by frontend as payload
    in order to initialize a new Quiz Session.
    """
    topic: str
    difficulty: str



class CreateSessionResponse(BaseModel):
    """
    Response returned upon successfully initializing a quiz session.
    Provides immediate payload to bootstrap the client feed.
    """
    topic: str
    difficulty: str
    score: int = Field(default=0)
    num_questions_delivered: int = Field(default=0)
    num_questions_correct: int = Field(default=0)
    num_questions_incorrect: int = Field(default=0)
    total_time_taken: int = Field(default=0)
    average_time_taken: int = Field(default=0)
    session_feedback: str = Field(default="Coming Soon")    # ai generated


class SubmitAnswerRequest(BaseModel):
    """
    Payload sent by the client when submitting an answer for evaluation.
    """
    question_id: str
    selected_option_index: int


class SubmitAnswerResponse(BaseModel):
    """
    Response returned after evaluating a submitted answer.
    """
    question_id: str
    is_correct: bool
    correct_option_index: int
    explanation: str
