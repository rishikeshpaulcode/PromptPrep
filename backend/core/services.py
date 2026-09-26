import asyncio
import core.chains as chains

class AIService:
    def __init__(self):
        self.question_batch_chain = chains.get_question_batch_chain()

    def generate_question_bach(self, topic, difficulty, count) -> list[dict]:
        # get list of generated questions
        question_batch = self.question_batch_chain.invoke({
            "topic": topic,
            "difficulty": difficulty,
            "count": count
        })

        # convert pydantic objects to json
        question_batch_json = []
        for question in question_batch.questions:
            question_batch_json.append(question.model_dump_json())

        return question_batch_json

