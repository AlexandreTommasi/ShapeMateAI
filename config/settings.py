# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações da API
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"  # ou "gpt-4" para mais capacidade

# Configurações do agente
TEMPERATURE = 0.7  # Aumenta criatividade nas respostas
MAX_TOKENS = 1000  # Limite de tokens na resposta
SYSTEM_ROLE = "Você é um assistente virtual amigável e prestativo. Responda de forma conversacional e natural."

