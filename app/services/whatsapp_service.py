"""
Servicio de WhatsApp Cloud API
"""
import httpx
from typing import Optional

from app.config import get_settings


class WhatsAppService:
    BASE_URL = "https://graph.facebook.com/v21.0"
    
    def __init__(self):
        self.settings = get_settings()
    
    async def send_text_message(self, to: str, text: str) -> dict:
        """Enviar mensaje de texto"""
        url = f"{self.BASE_URL}/{self.settings.whatsapp_phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.json()
    
    async def send_typing_indicator(self, to: str):
        """Enviar indicador de 'escribiendo...'"""
        url = f"{self.BASE_URL}/{self.settings.whatsapp_phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "reaction",
            "status": "typing"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, headers=headers, json=payload)
            except:
                pass  # Ignorar errores del typing indicator
    
    async def download_media(self, media_id: str) -> Optional[bytes]:
        """Descargar archivo multimedia (audio, imagen, etc.)"""
        # Paso 1: Obtener URL del media
        url = f"{self.BASE_URL}/{media_id}"
        headers = {"Authorization": f"Bearer {self.settings.whatsapp_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
            
            media_url = response.json().get("url")
            
            if not media_url:
                return None
            
            # Paso 2: Descargar el archivo
            media_response = await client.get(media_url, headers=headers)
            
            if media_response.status_code == 200:
                return media_response.content
            
            return None
    
    async def mark_as_read(self, message_id: str):
        """Marcar mensaje como leído"""
        url = f"{self.BASE_URL}/{self.settings.whatsapp_phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, headers=headers, json=payload)
            except:
                pass


# Instancia global
whatsapp_service = WhatsAppService()
