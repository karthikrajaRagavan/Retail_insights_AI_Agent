import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

print("\n" + "="*60)
print("  RETAIL INSIGHTS AGENT - Startup")
print("="*60)

from . import config
from .database.duckdb import get_connection
get_connection()

if config.PINECONE_API_KEY:
    print("  Pinecone: Configured (connects on first knowledge query)")
else:
    print("  Pinecone: Not configured (knowledge agent disabled)")

from .agents import root_agent

print("="*60)
print("  RETAIL INSIGHTS AGENT - Ready!")
print("="*60 + "\n")

__all__ = ["root_agent"]
