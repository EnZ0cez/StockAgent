from langchain_openai import ChatOpenAI
from src.config import settings

def get_llm():
    """Initialize and return DeepSeek LLM instance"""
    return ChatOpenAI(
        model=settings.deepseek_model,
        openai_api_key=settings.deepseek_api_key,
        openai_api_base=settings.deepseek_base_url,
        temperature=settings.deepseek_temperature,
        max_tokens=settings.deepseek_max_tokens,
        streaming=False
    )