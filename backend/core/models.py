# creates and returns ai models

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from core.schemas import LLMQuizBatch, LLMSessionFeedback

load_dotenv()


def get_base_model(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=temperature,
        timeout=30,
    )


def get_question_batch_model(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    return get_base_model(temperature).with_structured_output(LLMQuizBatch)


def get_session_feedback_model(
    temperature: float = 0.2,
) -> ChatGoogleGenerativeAI:
    """Create a low-temperature model for structured session feedback."""
    return get_base_model(temperature).with_structured_output(LLMSessionFeedback)
