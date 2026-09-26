# FastAPI application
# testing
from core.services import AIService

ai_service = AIService()

question_batch = ai_service.generate_question_bach(
    topic="Newtons Laws of Motion",
    difficulty="easy",
    count=3
)

print(question_batch)
