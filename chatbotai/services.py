from langchain_google_genai import ChatGoogleGenerativeAI
from django.conf import settings


class LLMService:
    _llm = None

    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            cls._llm = ChatGoogleGenerativeAI(
                google_api_key=settings.GOOGLE_API_KEY,
                model="gemini-2.5-flash",
                temperature=0.7,
            )
        return cls._llm
