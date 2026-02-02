from google.adk.agents import LlmAgent

from ...tools import search_knowledge_base
from ...config import PIPELINE_AGENT_MODEL

retrieval_agent = LlmAgent(
    name="retrieval_agent",
    model=PIPELINE_AGENT_MODEL,

    description=(
        "Searches the knowledge base for documents relevant to the user's question. "
        "Expert at formulating search queries for optimal retrieval."
    ),

    instruction="""You are a document retrieval specialist.

Your task is to search the knowledge base for relevant information.

STEPS:
1. Analyze the user's question to identify key concepts
2. Call search_knowledge_base with the search query
3. Return the search results

SEARCH STRATEGY:
- Use natural language queries, not keywords
- Focus on the main topic (returns, shipping, product info)
- Include relevant context from the question

Output the search results directly.""",

    tools=[search_knowledge_base],
    output_key="retrieved_documents",
)
