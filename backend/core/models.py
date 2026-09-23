# created and returns ai models
from langchain_google_genai import ChatGoogleGenerativeAI
from schemas import QuestionInternal
from dotenv import load_dotenv

load_dotenv()
 
def get_base_model(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=temperature,
        timeout=30
    )

def get_structured_model(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    return get_base_model(temperature).with_structured_output(QuestionInternal)
