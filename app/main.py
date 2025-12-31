"""
Loopera WhatsApp Bot - Aplicación Principal
"""
import hmac
import hashlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse

from app.config import get_settings
from app.services import session_manager, whatsapp_service, groq_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando Loopera WhatsApp Bot...")

    # Conexión a Redis no bloqueante
    try:
        await session_manager.connect()
        logger.info("✅ Conectado a Redis")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo conectar a Redis: {e}")
        logger.warning("El bot funcionará sin persistencia de sesiones")

    yield

    # Shutdown
    logger.info("👋 Cerrando conexiones...")
    try:
        await session_manager.disconnect()
    except Exception:
        pass


app = FastAPI(
    title="Loopera WhatsApp Bot",
    description="Bot de WhatsApp para Loopera - Desarrollo de Agentes AI",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Loopera WhatsApp Bot",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check para Railway"""
    return {"status": "healthy"}


@app.get("/webhook")
@app.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    """
    Verificación del webhook de WhatsApp (requerido por Meta)
    """
    settings = get_settings()

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.webhook_verify_token:
        logger.info("✅ Webhook verificado exitosamente")
        return PlainTextResponse(content=challenge)

    logger.warning("❌ Verificación de webhook fallida")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
@app.post("/webhook/whatsapp")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    # PRIMER LOG - antes de todo
    logger.info("🚨🚨🚨 POST RECIBIDO EN WEBHOOK 🚨🚨🚨")

    try:
        body = await request.json()
        logger.info(f"📦 Body recibido: {str(body)[:500]}")

        # Extraer información del mensaje
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        # Verificar si hay mensajes
        messages = value.get("messages", [])

        if not messages:
            # Puede ser una actualización de estado, ignorar
            logger.info("ℹ️ Webhook sin mensajes (posible status update)")
            return {"status": "ok"}
        
        message = messages[0]
        
        # Extraer datos del mensaje
        phone = message.get("from")
        message_id = message.get("id")
        message_type = message.get("type")
        
        logger.info(f"📩 Mensaje recibido de {phone} - Tipo: {message_type}")
        
        # Procesar en background para responder rápido a Meta
        background_tasks.add_task(
            process_message,
            phone=phone,
            message=message,
            message_type=message_type,
            message_id=message_id
        )
        
        # Responder inmediatamente a Meta (< 3 segundos)
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        # Aún así retornar 200 para evitar reintentos de Meta
        return {"status": "ok"}


async def process_message(
    phone: str,
    message: dict,
    message_type: str,
    message_id: str
):
    """
    Procesar mensaje en background
    """
    try:
        # Marcar como leído
        await whatsapp_service.mark_as_read(message_id)
        
        # Extraer texto según el tipo de mensaje
        user_text = await extract_message_content(message, message_type)
        
        if not user_text:
            await whatsapp_service.send_text_message(
                phone,
                "Lo siento, no pude procesar ese tipo de mensaje. ¿Podrías escribirme o enviarme una nota de voz?"
            )
            return
        
        logger.info(f"💬 Texto extraído: {user_text[:100]}...")
        
        # Obtener historial de conversación
        session = await session_manager.get_session(phone)
        history = session.get("history", [])
        
        # Generar respuesta con LLM
        response = await groq_service.chat(
            user_message=user_text,
            conversation_history=history
        )
        
        logger.info(f"🤖 Respuesta generada: {response[:100]}...")
        
        # Enviar respuesta
        await whatsapp_service.send_text_message(phone, response)
        
        # Actualizar sesión
        await session_manager.update_session(
            phone=phone,
            user_message=user_text,
            bot_response=response,
            metadata={"last_message_type": message_type}
        )
        
        logger.info(f"✅ Mensaje procesado para {phone}")
    
    except Exception as e:
        logger.error(f"Error procesando mensaje de {phone}: {e}")
        
        # Intentar enviar mensaje de error al usuario
        try:
            await whatsapp_service.send_text_message(
                phone,
                "Disculpa, tuve un problema procesando tu mensaje. ¿Podrías intentar de nuevo?"
            )
        except:
            pass


async def extract_message_content(message: dict, message_type: str) -> str:
    """
    Extraer contenido del mensaje según su tipo
    """
    if message_type == "text":
        return message.get("text", {}).get("body", "")
    
    elif message_type == "audio":
        # Transcribir nota de voz
        audio_id = message.get("audio", {}).get("id")
        
        if not audio_id:
            return None
        
        logger.info(f"🎤 Descargando audio {audio_id}...")
        
        # Descargar audio
        audio_bytes = await whatsapp_service.download_media(audio_id)
        
        if not audio_bytes:
            logger.error("No se pudo descargar el audio")
            return None
        
        logger.info(f"🎤 Transcribiendo audio ({len(audio_bytes)} bytes)...")
        
        # Transcribir
        transcription = await groq_service.transcribe_audio(audio_bytes)
        
        logger.info(f"🎤 Transcripción: {transcription[:100]}...")
        
        return transcription
    
    elif message_type == "image":
        # Por ahora solo texto de caption si existe
        return message.get("image", {}).get("caption", "[Imagen recibida]")
    
    elif message_type == "document":
        return message.get("document", {}).get("caption", "[Documento recibido]")
    
    elif message_type == "sticker":
        return "[Sticker recibido] 😊"
    
    elif message_type == "location":
        return "[Ubicación compartida]"
    
    elif message_type == "contacts":
        return "[Contacto compartido]"
    
    else:
        return None


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"🔍 Starting on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
