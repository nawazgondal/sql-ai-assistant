import os
from dotenv import load_dotenv

load_dotenv()

# Ollama Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# Database Settings
DATABASE_PATH = os.getenv("DATABASE_PATH", "data.db")
DATABASE_TIMEOUT = int(os.getenv("DATABASE_TIMEOUT", "30"))

# AI Settings
CACHE_TTL = int(os.getenv("AI_CACHE_TTL", "3600"))
RETRY_ATTEMPTS = int(os.getenv("AI_RETRY_ATTEMPTS", "3"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
