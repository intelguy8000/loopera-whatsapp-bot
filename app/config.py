"""
Configuración del bot - carga variables de entorno
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # WhatsApp Cloud API
    whatsapp_token: str = ""
    whatsapp_phone_id: str = ""
    webhook_verify_token: str = "loopera-verify-token-2024"
    
    # Groq API (Whisper + LLM)
    groq_api_key: str = ""
    
    # Redis (Railway provee esta variable automáticamente)
    redis_url: str = "redis://localhost:6379"
    
    # Configuración del bot
    business_name: str = "Loopera"
    business_description: str = "Desarrollo de Agentes AI para empresas"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
