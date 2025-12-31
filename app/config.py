"""
Configuración del bot - carga variables de entorno
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # WhatsApp Cloud API
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""  # Acepta WHATSAPP_PHONE_NUMBER_ID
    whatsapp_phone_id: str = ""  # Acepta WHATSAPP_PHONE_ID (alias)
    webhook_verify_token: str = "loopera-verify-token-2024"

    @property
    def phone_id(self) -> str:
        """Retorna el phone_id desde cualquiera de las dos variables"""
        return self.whatsapp_phone_number_id or self.whatsapp_phone_id
    
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
