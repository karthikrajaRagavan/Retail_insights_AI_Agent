from google.adk.agents import LlmAgent

from ...tools import execute_sql
from ...config import PIPELINE_AGENT_MODEL

data_extraction_agent = LlmAgent(
    name="data_extraction_agent",
    model=PIPELINE_AGENT_MODEL,

    description=(
        "Executes SQL queries against the retail database and retrieves data. "
        "Handles query execution and returns raw results."
    ),

    instruction="""You are a data extraction specialist.

Your job is to execute the SQL query and retrieve the data.

STEPS:
1. Read the SQL query from the previous step (it will be provided to you)
2. Use the execute_sql tool to run the query
3. Return the results exactly as received

INPUT: You will receive a SQL query to execute.

IMPORTANT:
- Execute the SQL query exactly as provided
- Do not modify the query
- Return the raw results from the execute_sql tool
- Include the data, columns, and row count in your response

If the query execution fails, report the error clearly.""",

    tools=[execute_sql],
    output_key="query_results",
)
