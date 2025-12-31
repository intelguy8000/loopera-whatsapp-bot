"""
Servicio de WhatsApp Cloud API
"""
import logging
import httpx
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    BASE_URL = "https://graph.facebook.com/v21.0"

    def __init__(self):
        self.settings = get_settings()
        # Log de verificación de config
        token = self.settings.whatsapp_token
        phone_id = self.settings.whatsapp_phone_number_id
        logger.info(f"📱 WhatsApp Config - Token: {token[:20]}... | Phone ID: {phone_id}")

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

        logger.info(f"📤 Enviando mensaje a {to}")
        logger.info(f"📤 URL: {url}")
        logger.info(f"📤 Payload: {payload}")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

            # Log completo de la respuesta
            logger.info(f"📥 Status Code: {response.status_code}")
            logger.info(f"📥 Response Body: {response.text}")

            if response.status_code != 200:
                logger.error(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")

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
