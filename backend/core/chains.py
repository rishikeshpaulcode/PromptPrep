# all runnable chains

from core.models import get_question_batch_model, get_session_feedback_model
from core.prompts import generate_question_batch_prompt, get_session_feedback_prompt


def get_question_batch_chain():
    model = get_question_batch_model()
    return generate_question_batch_prompt | model


def get_session_feedback_chain():
    """Build the chain that generates structured AI session feedback."""
    model = get_session_feedback_model()
    return get_session_feedback_prompt | model
