# config.py
import os
from agno.models.openai import OpenAIResponses
from agno.knowledge.embedder.openai import OpenAIEmbedder
from dotenv import load_dotenv

load_dotenv()

# Utilisation de text-embedding-3-small comme dans le zip
embedder = OpenAIEmbedder(id="text-embedding-3-small")
model = OpenAIResponses(id=os.getenv("AI_MODEL", "gpt-4o-mini"))

PG_USER = os.getenv("PG_USER", "ai")
PG_PASSWORD = os.getenv("PG_PASSWORD", "ai")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5532")
PG_DBNAME = os.getenv("PG_DBNAME", "ai")

db_url = f"postgresql+psycopg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}"
