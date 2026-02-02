from google.adk.agents import SequentialAgent

from .retrieval import retrieval_agent
from .synthesis import synthesis_agent

knowledge_agent = SequentialAgent(
    name="knowledge_agent",

    description=(
        "Knowledge agent that answers questions about policies, FAQs, and product information. "
        "Retrieves relevant documents from the knowledge base and synthesizes helpful answers."
    ),

    sub_agents=[
        retrieval_agent,
        synthesis_agent,
    ],
)
