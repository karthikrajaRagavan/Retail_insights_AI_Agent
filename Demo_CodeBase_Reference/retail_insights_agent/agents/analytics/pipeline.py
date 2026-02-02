from google.adk.agents import SequentialAgent

from .query_resolution import query_resolution_agent
from .data_extraction import data_extraction_agent
from .response_validation import response_validation_agent

analytics_agent = SequentialAgent(
    name="analytics_agent",

    description=(
        "Analytics agent that processes business questions about retail data. "
        "Interprets queries, retrieves data, and delivers formatted insights."
    ),

    sub_agents=[
        query_resolution_agent,
        data_extraction_agent,
        response_validation_agent,
    ],
)
