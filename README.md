# 🤖 Loopera WhatsApp Bot

Bot de WhatsApp AI para Loopera - Desarrollo de Agentes AI para empresas.

## 🚀 Características

- ✅ Recibe y responde mensajes de texto
- ✅ Procesa notas de voz (transcripción con Whisper)
- ✅ Mantiene contexto de conversación (Redis)
- ✅ LLM inteligente para respuestas naturales (Groq)
- ✅ Específico para el negocio (cumple políticas Meta 2026)

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI
- **LLM**: Groq (Llama 3.3 70B)
- **Transcripción**: Groq Whisper Large V3 Turbo
- **Sesiones**: Redis
- **Hosting**: Railway
- **Audio**: ffmpeg

## 📋 Requisitos

- Python 3.11+
- Cuenta de WhatsApp Business API (WABA)
- API Key de Groq
- Redis (incluido en Railway)

## 🔧 Variables de Entorno

```env
# WhatsApp Cloud API
WHATSAPP_TOKEN=tu_token
WHATSAPP_PHONE_ID=tu_phone_id
WEBHOOK_VERIFY_TOKEN=tu_token_verificacion

# Groq
GROQ_API_KEY=tu_api_key

# Redis (Railway lo provee)
REDIS_URL=redis://...
```

## 🚀 Deploy en Railway

1. Fork este repositorio
2. Conecta tu repo en Railway
3. Agrega las variables de entorno
4. Railway detectará el Dockerfile automáticamente

## 📁 Estructura

```
loopera-whatsapp-bot/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI + Webhook
│   ├── config.py        # Configuración
│   └── services/
│       ├── __init__.py
│       ├── redis_service.py    # Sesiones
│       ├── whatsapp_service.py # WhatsApp API
│       └── groq_service.py     # LLM + Whisper
├── Dockerfile
├── requirements.txt
├── railway.json
└── README.md
```

## 🔒 Seguridad

- Las API keys NUNCA se suben al repositorio
- El webhook valida firma de Meta
- Sesiones expiran en 24 horas
- Bot restringido al dominio del negocio

## 📄 Licencia

Privado - Loopera © 2024
