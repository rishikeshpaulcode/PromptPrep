import asyncio
import core.chains as chains
from core.schemas import QuestionInternal

class AIService:
    def __init__(self):
        self.question_batch_chain = chains.get_question_batch_chain()

    def generate_question_batch(self, topic: str, difficulty: str, count: int = 5) -> list[QuestionInternal]:
        question_batch = self.question_batch_chain.invoke({
            "topic": topic,
            "difficulty": difficulty,
            "count": count
        })

        return question_batch.questions

