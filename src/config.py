import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Keys
    deepseek_api_key: str
    tavily_api_key: str
    financial_datasets_api_key: Optional[str] = None
    
    # LLM Configuration
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_temperature: float = 0.1
    deepseek_max_tokens: int = 4000
    
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
    required_keys = ["deepseek_api_key", "tavily_api_key"]
    missing_keys = []
    
    for key in required_keys:
        if not getattr(settings, key):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return True