# Feature: AI Session Feedback

## Requirement
When a user has completed their quiz, they are shown an AI Session Feedback section. This section should include:
- A list of all weak concepts.
- Pinpoint the exact topic where user is having knowledge gap.
- 1 or 2 tips on how to improve that concept.


## Design
### New components:
- **LLMWeakConcept** pydantic model which has two fields: "concept": indicates the weak concept, "advice": 1 or 2 tips on how to improve that concept.
- **LLMSessionFeedback** pydantic model will hold a list of LLMWeakConcept.
- A new **Model** that returns result in LLMSessionFeedback structred format using Gemini API (use low temperature).
- A new **Prompt Template** that must have a clear and concise prompt to be fed to the Model. The prompt must take a list of incorrect question_texts and topic of quiz as input.
- A new **Chain** that must return AI feedback when invoked (use newly created model and prompt).
- In **AIService**, a new method get_session_feedback().
- A new **Redis Key** f"session:{session_id}:incorrect-questions" (holds a list of question_text for incorrect questions)
- A new **API Endpoint** that returns AI feedback in LLMSessionFeedback format.

### Components affected:
- **/api/check_answer** API Endpoint: if user answered a question wrong, add its question_text to f"session:{session_id}:incorrect-questions" Redis key.

### Data flow:
1. Whenever a user answers a question wrong, its question_text is stored in Redis key.
2. After the user ends their quiz session, the AI feedback API endpoint reads the list of incorrect question_text(s) using the session_id.
3. If the list of questions is empty, return a Good Job / Keep it Up message.
4. It internally used AIService method get_session_feedback().
5. Finally the API endpoint returns the feedback a per the LLMSessionFeedback model.


## Out of scope
- Calculating final score.
- Generating the entire session summary.
- Providing overall study tips.