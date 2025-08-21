import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    qwen_api_key: str
    tavily_api_key: str
    alpha_vantage_api_key: str  # Alpha Vantage API key (required)
    financial_datasets_api_key: Optional[str] = None
    
    # LLM Configuration
    qwen_model: str = "qwen-turbo"
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_temperature: float = 0.1
    qwen_max_tokens: int = 4000
    
    # Agent Configuration
    max_agent_iterations: int = 10
    timeout_seconds: int = 30
    
    # Data Sources
    default_stock_symbol: str = "AAPL"
    default_time_period: str = "1y"
    default_news_days: int = 7
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()

def validate_settings():
    """Validate that required settings are present"""
    required_keys = ["qwen_api_key", "tavily_api_key"]
    missing_keys = []
    
    for key in required_keys:
        if not getattr(settings, key):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return True