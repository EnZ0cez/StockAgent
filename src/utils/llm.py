import sys
import os

# Add the src directory to the Python path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from langchain_openai import ChatOpenAI
from src.config import settings

def get_llm():
    """Initialize and return Qwen LLM instance"""
    try:
        import httpx
        
        # 创建一个禁用代理的 HTTP 客户端
        http_client = httpx.Client(
            proxy=None,  # 禁用代理
            verify=True,  # 启用 SSL 验证
            timeout=30.0  # 设置超时
        )
        
        return ChatOpenAI(
            model=settings.qwen_model,
            openai_api_key=settings.qwen_api_key,
            openai_api_base=settings.qwen_base_url,
            temperature=settings.qwen_temperature,
            max_tokens=settings.qwen_max_tokens,
            streaming=False,
            http_client=http_client
        )
    except Exception as e:
        print(f"LLM 初始化错误: {e}")
        # 如果自定义客户端失败，尝试默认配置
        return ChatOpenAI(
            model=settings.qwen_model,
            openai_api_key=settings.qwen_api_key,
            openai_api_base=settings.qwen_base_url,
            temperature=settings.qwen_temperature,
            max_tokens=settings.qwen_max_tokens,
            streaming=False
        )