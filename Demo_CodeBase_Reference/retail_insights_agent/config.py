import os
from pathlib import Path
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).parent
REPO_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(REPO_ROOT / ".env")

# Google Cloud / Vertex AI
SERVICE_ACCOUNT_FILE = REPO_ROOT / os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
if SERVICE_ACCOUNT_FILE.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SERVICE_ACCOUNT_FILE)

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", os.getenv("GOOGLE_CLOUD_PROJECT", ""))
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))

# OpenAI (PandasAI + NeMo Guardrails)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Gemini (ADK Agents)
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gemini-3-flash-preview")
PIPELINE_AGENT_MODEL = os.getenv("PIPELINE_AGENT_MODEL", "gemini-2.5-flash-lite-preview-09-2025")

# Guardrails
GUARDRAILS_BLOCKED_MESSAGE = """I can help with sales analytics and customer support (returns, shipping, product info). Please ask about these topics."""

# Pinecone (Knowledge Base)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "")
PINECONE_HOST = os.getenv("PINECONE_HOST", "")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "candescent-retail-kb")

# Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

# Document Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Retrieval
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))

# Table Schema
TABLE_SCHEMAS = {
    "amazon_sales": {
        "source_file": "Amazon Sale Report.csv",
        "description": "Amazon India order transactions (128K rows, Apr-Jun 2022)",
        "column_mapping": {
            "Order ID": "order_id",
            "Date": "order_date",
            "Status": "status",
            "Fulfilment": "fulfilment",
            "Style": "style",
            "SKU": "sku",
            "Category": "category",
            "Size": "size",
            "Qty": "quantity",
            "Amount": "amount",
            "ship-city": "city",
            "ship-state": "state",
            "B2B": "is_b2b",
        },
        "field_descriptions": {
            "order_id": "Unique Amazon order identifier",
            "order_date": "Order date (MM-DD-YY format)",
            "status": "Order status: Shipped, Cancelled, Pending, Delivered, etc.",
            "fulfilment": "Fulfilment type: Amazon or Merchant",
            "style": "Product style code",
            "sku": "Stock keeping unit",
            "category": "Product category: kurta, Set, Top, Western Dress, Blouse, etc.",
            "size": "Product size: XS, S, M, L, XL, XXL, 3XL, etc.",
            "quantity": "Quantity ordered",
            "amount": "Order amount in INR (null for cancelled orders)",
            "city": "Shipping city",
            "state": "Shipping state (Indian states)",
            "is_b2b": "Business-to-business order flag (True/False)",
        },
    },
}


def get_schema_summary() -> str:
    lines = []
    for table_name, schema in TABLE_SCHEMAS.items():
        cols = list(schema["column_mapping"].values())
        lines.append(f"- {table_name}: {schema['description']}")
        lines.append(f"  Columns: {', '.join(cols[:8])}...")
    return "\n".join(lines)
