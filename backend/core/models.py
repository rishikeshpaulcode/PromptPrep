from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from core.schemas import LLMQuizBatch, LLMSessionFeedback

load_dotenv()

NVIDIA_MODEL = "mistralai/mistral-large-4-1t-a52b"


def get_base_model(temperature: float = 0.7) -> ChatNVIDIA:
    """Create a NVIDIA NIM chat model with the configured Mistral model."""
    return ChatNVIDIA(
        model=NVIDIA_MODEL,
        temperature=temperature,
    )


def get_question_batch_model(temperature: float = 0.7) -> ChatNVIDIA:
    """Create the structured question-batch model."""
    return get_base_model(temperature).with_structured_output(LLMQuizBatch)


def get_session_feedback_model(
    temperature: float = 0.2,
) -> ChatNVIDIA:
    """Create a low-temperature model for structured session feedback."""
    return get_base_model(temperature).with_structured_output(LLMSessionFeedback)
