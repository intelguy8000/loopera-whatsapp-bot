"""
Servicio de Groq para transcripción de audio (Whisper) y LLM
"""
import tempfile
import subprocess
from pathlib import Path
from groq import Groq

from app.config import get_settings


class GroqService:
    def __init__(self):
        self.settings = get_settings()
        self.client = None
    
    def _get_client(self) -> Groq:
        """Obtener cliente de Groq (lazy loading)"""
        if not self.client:
            self.client = Groq(api_key=self.settings.groq_api_key)
        return self.client
    
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribir audio usando Whisper de Groq
        
        Args:
            audio_bytes: Bytes del archivo de audio (OGG/Opus de WhatsApp)
        
        Returns:
            Texto transcrito
        """
        client = self._get_client()
        
        # Guardar audio temporalmente
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_ogg:
            temp_ogg.write(audio_bytes)
            temp_ogg_path = temp_ogg.name
        
        try:
            # Convertir OGG a MP3 (mejor compatibilidad con Whisper)
            temp_mp3_path = temp_ogg_path.replace(".ogg", ".mp3")
            
            subprocess.run([
                "ffmpeg", "-i", temp_ogg_path,
                "-acodec", "libmp3lame",
                "-ar", "16000",
                "-ac", "1",
                temp_mp3_path,
                "-y"
            ], check=True, capture_output=True)
            
            # Transcribir con Whisper
            with open(temp_mp3_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_file,
                    language="es"
                )
            
            return transcription.text
        
        finally:
            # Limpiar archivos temporales
            Path(temp_ogg_path).unlink(missing_ok=True)
            Path(temp_mp3_path).unlink(missing_ok=True)
    
    async def chat(
        self, 
        user_message: str, 
        conversation_history: list = None,
        system_prompt: str = None
    ) -> str:
        """
        Generar respuesta usando LLM de Groq
        
        Args:
            user_message: Mensaje del usuario
            conversation_history: Historial de conversación previo
            system_prompt: Prompt del sistema personalizado
        
        Returns:
            Respuesta del bot
        """
        client = self._get_client()
        
        # System prompt por defecto para Loopera
        if not system_prompt:
            system_prompt = self._get_loopera_system_prompt()
        
        # Construir mensajes
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar historial si existe
        if conversation_history:
            messages.extend(conversation_history)
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": user_message})
        
        # Generar respuesta
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return completion.choices[0].message.content
    
    def _get_loopera_system_prompt(self) -> str:
        """System prompt específico para Loopera"""
        return f"""Eres el asistente virtual de {self.settings.business_name}, especializado en {self.settings.business_description}.

SOBRE LOOPERA:
- Somos una consultora especializada en desarrollo de Agentes AI para empresas
- Ayudamos a empresas a automatizar su atención al cliente con bots inteligentes de WhatsApp
- Nuestros servicios incluyen: diseño, desarrollo, implementación y mantenimiento de agentes AI
- Trabajamos principalmente con empresas en Colombia y Latinoamérica

REGLAS DE CONVERSACIÓN:
1. SOLO respondes sobre: servicios de Loopera, agentes AI, automatización, precios, proceso de trabajo
2. Si preguntan algo fuera de tu dominio, di: "Solo puedo ayudarte con temas relacionados a desarrollo de agentes AI. ¿Te gustaría saber cómo podemos ayudar a tu empresa?"
3. NUNCA respondas sobre: política, deportes, noticias, conocimiento general, chismes
4. Si no tienes información específica, ofrece conectar con un asesor humano
5. Siempre identifícate como asistente virtual de Loopera
6. Sé amable, profesional y conciso
7. Usa español natural, como se habla en Colombia

FLUJO DE CONVERSACIÓN:
- Si es un prospecto nuevo: Pregunta sobre su empresa, qué problema quiere resolver, qué volumen de mensajes manejan
- Si quiere información de precios: Explica que los precios varían según complejidad y ofrece agendar una llamada
- Si es cliente existente: Pregunta cómo puedes ayudarlo y ofrece conectar con su asesor asignado

CONTACTO:
- Para agendar una llamada: "Te puedo conectar con nuestro equipo para agendar una demostración"
- WhatsApp de soporte: Ofrece escalar a un humano si no puedes resolver

Responde de forma natural y conversacional, sin usar markdown ni formatos especiales."""


# Instancia global
groq_service = GroqService()
