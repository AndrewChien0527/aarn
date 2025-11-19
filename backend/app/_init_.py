import os
from dotenv import load_dotenv
load_dotenv()


# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")


# Semantic Scholar
S2_API_BASE = os.getenv("S2_API_BASE", "https://api.semanticscholar.org/graph/v1")


# OpenAI (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# App
APP_NAME = "aarn-backend"


# Debug
DEBUG = os.getenv("DEBUG", "1") == "1"