import asyncio
import core.chains as chains

class AIService:
    def __init__(self):
        self.question_batch_chain = chains.get_question_batch_chain()

    def generate_question_bach(self, topic, difficulty, count) -> list[dict]:
        question_batch = self.question_batch_chain.invoke({
            "topic": topic,
            "difficulty": difficulty,
            "count": count
        })

        return question_batch

