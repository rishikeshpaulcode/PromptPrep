# all runnable chains

from core.models import get_structured_model
from core.prompts import generate_question_batch_prompt

def get_question_batch_chain():
    model = get_structured_model()
    return generate_question_batch_prompt | model
