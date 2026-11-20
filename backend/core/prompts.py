# contains all the promt templates

from langchain_core.prompts import PromptTemplate

# Infinite Quiz Reel System Prompt Template Text
QUIZ_REEL_PROMPT_TEMPLATE = """
    You are an expert educational content designer specializing in creating highly engaging, accurate, and fair multiple-choice questions for a multiple choice quiz.

    ### CONTEXT & PARAMETERS
    - **Topic**: {topic},
    - **Difficulty Level**: {difficulty}

    ### STRICT GENERATION RULES
    - Question must be factually accurate with unambiguous correct answers.
    - Avoid trick questions, double negatives, or opinion-based statements.
    - Provide EXACTLY 4 options per question.
    - Ensure options are mutually exclusive and roughly equal in length.
    - Distractors (incorrect choices) must be plausible, realistic, and relevant.
    - Provide a clear explanation (3-4 sentences) detailing why the correct option is right and why others are wrong.

    ### DIFFICULTY GUIDELINES
    - easy: Fundamental terminology, basic concepts, high recognizability.
    - medium: Applied knowledge, conceptual understanding, multi-step reasoning.
    - hard: Edge cases, nuanced mechanics, subtle distinctions, advanced troubleshooting.

    Generate the question strictly according to the specified output schema.
"""

SESSION_FEEDBACK_PROMPT_TEMPLATE = """
You are an expert educational coach reviewing a student's quiz performance.

Quiz topic: {topic}
Incorrect question texts:
{incorrect_question_texts}

Identify every distinct, precise knowledge gap demonstrated by the incorrect
questions. For each weak concept, provide one or two practical tips that will
help the student improve that concept.
"""


# Instantiate the PromptTemplate
generate_question_batch_prompt = PromptTemplate(
    template=QUIZ_REEL_PROMPT_TEMPLATE,
    input_variables=["topic", "difficulty", "count"]
)

get_session_feedback_prompt = PromptTemplate(
    template=SESSION_FEEDBACK_PROMPT_TEMPLATE,
    input_variables=["topic", "incorrect_question_texts"],
)
