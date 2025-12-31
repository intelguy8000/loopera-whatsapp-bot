"""
Servicio de Redis para sesiones de conversación
"""
import json
import redis.asyncio as redis
from typing import Optional
from datetime import datetime

from app.config import get_settings


class SessionManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.ttl = 86400  # 24 horas
    
    async def connect(self):
        """Conectar a Redis"""
        settings = get_settings()
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Desconectar de Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get_session(self, phone: str) -> dict:
        """Obtener sesión de un usuario"""
        if not self.redis:
            return self._empty_session()
        
        key = f"session:{phone}"
        data = await self.redis.get(key)
        
        if data:
            return json.loads(data)
        
        return self._empty_session()
    
    async def update_session(
        self, 
        phone: str, 
        user_message: str, 
        bot_response: str,
        metadata: dict = None
    ):
        """Actualizar sesión con nuevo intercambio"""
        if not self.redis:
            return
        
        key = f"session:{phone}"
        session = await self.get_session(phone)
        
        # Agregar mensajes al historial
        session["history"].append({"role": "user", "content": user_message})
        session["history"].append({"role": "assistant", "content": bot_response})
        
        # Mantener solo últimos 10 intercambios (20 mensajes)
        session["history"] = session["history"][-20:]
        
        # Actualizar metadata
        session["updated_at"] = datetime.utcnow().isoformat()
        if metadata:
            session["metadata"].update(metadata)
        
        # Guardar
        await self.redis.setex(key, self.ttl, json.dumps(session))
    
    async def clear_session(self, phone: str):
        """Limpiar sesión de un usuario"""
        if not self.redis:
            return
        
        key = f"session:{phone}"
        await self.redis.delete(key)
    
    def _empty_session(self) -> dict:
        """Sesión vacía por defecto"""
        return {
            "history": [],
            "metadata": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }


# Instancia global
session_manager = SessionManager()
