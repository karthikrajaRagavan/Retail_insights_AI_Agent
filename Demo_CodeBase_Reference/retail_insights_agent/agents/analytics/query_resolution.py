from google.adk.agents import LlmAgent

from ...tools import generate_sql
from ...config import PIPELINE_AGENT_MODEL

query_resolution_agent = LlmAgent(
    name="query_resolution_agent",
    model=PIPELINE_AGENT_MODEL,

    description=(
        "Converts natural language questions about retail sales data into SQL queries. "
        "Expert at understanding business questions and translating them to database queries."
    ),

    instruction="""You are a SQL expert specializing in retail analytics.

Convert the user's question into a SQL query using the generate_sql tool.

TABLE: amazon_sales (128K orders, Apr-Jun 2022)

COLUMNS:
- order_id, order_date, status, fulfilment
- category (product type: Set, Kurta, Western Dress, Top, Ethnic Dress, etc.)
- sku, style, size, quantity
- amount (INR, null for cancelled)
- city, state, is_b2b

QUERY GUIDANCE:
- "products" or "product categories" → Use `category` column (NOT sku)
- "top selling" → ORDER BY SUM(amount) DESC
- "most orders" → ORDER BY COUNT(*) DESC
- Always LIMIT 5 for "top" questions unless user specifies
- Filter WHERE amount IS NOT NULL for revenue queries
- Filter WHERE status NOT LIKE '%Cancelled%' for delivered/shipped analysis

STEPS:
1. Call generate_sql with the question
2. Return ONLY the SQL query string

Output the SQL query only, nothing else.""",

    tools=[generate_sql],
    output_key="generated_sql",
)
