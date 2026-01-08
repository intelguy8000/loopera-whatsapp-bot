# Loopera WhatsApp Bot

Bot de WhatsApp AI para Loopera - Desarrollo de Agentes AI para empresas.

## Características

- Recibe y responde mensajes de texto
- Procesa notas de voz (transcripcion con Whisper)
- Mantiene contexto de conversacion (Redis)
- LLM inteligente para respuestas naturales (Groq)
- Especifico para el negocio (cumple politicas Meta 2026)

## Stack Tecnologico

- **Framework**: FastAPI
- **LLM**: Groq (Llama 3.3 70B)
- **Transcripcion**: Groq Whisper Large V3 Turbo
- **Sesiones**: Redis
- **Hosting**: Render / Railway (Nixpacks)

## Requisitos

- Python 3.11+
- Cuenta de WhatsApp Business API (WABA)
- API Key de Groq
- Redis

## Variables de Entorno

```env
# WhatsApp Cloud API
WHATSAPP_TOKEN=tu_token
WHATSAPP_PHONE_ID=949507764911133
WEBHOOK_VERIFY_TOKEN=loopera-verify-token-2024

# Groq
GROQ_API_KEY=gsk_xxx

# Redis
REDIS_URL=redis://...
```

## Deploy en Render/Railway

1. Conecta el repo de GitHub
2. Agrega las variables de entorno
3. El servicio detecta automaticamente FastAPI (Nixpacks)
4. Configura el webhook en Meta: `https://tu-app.onrender.com/webhook`

## Estructura

```
loopera-whatsapp-bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI + Webhook
│   ├── config.py            # Configuracion
│   └── services/
│       ├── __init__.py
│       ├── redis_service.py     # Sesiones
│       ├── whatsapp_service.py  # WhatsApp API
│       └── groq_service.py      # LLM + Whisper
├── Procfile                 # Comando de inicio
├── requirements.txt
└── README.md
```

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| GET | `/webhook` | Verificacion Meta |
| POST | `/webhook` | Recibir mensajes |

## Seguridad

- Las API keys NUNCA se suben al repositorio
- El webhook valida token de Meta
- Sesiones expiran en 24 horas
- Bot restringido al dominio del negocio

## Licencia

Privado - Loopera 2024
