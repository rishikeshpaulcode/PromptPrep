# interface (as a class) to access AI functionalities

import asyncio

import core.chains as chains
from core.schemas import LLMQuizBatch, LLMSessionFeedback


class AIService:
    def __init__(self):
        self.question_batch_chain = chains.get_question_batch_chain()
        self.session_feedback_chain = chains.get_session_feedback_chain()

    def generate_question_batch(
        self, topic: str, difficulty: str, count: int = 5
    ) -> LLMQuizBatch:
        """
        Generates a set of N questions on demand.
        Parameters: topic, difficulty, count (default = 5)
        """
        question_batch = self.question_batch_chain.invoke({
            "topic": topic,
            "difficulty": difficulty,
            "count": count
        })

        return question_batch

    def get_session_feedback(
        self, topic: str, incorrect_question_texts: list[str]
    ) -> LLMSessionFeedback:
        """Generate structured feedback from the session's incorrect questions."""
        return self.session_feedback_chain.invoke({
            "topic": topic,
            "incorrect_question_texts": incorrect_question_texts,
        })

