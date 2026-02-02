import logging
import re

logger = logging.getLogger(__name__)

# MVP: Keyword-based classification for fast, deterministic routing without LLM latency.
# Production: Can upgrade to LLM-based classifier for better accuracy on ambiguous queries.

ANALYTICS_KEYWORDS = [
    "revenue", "sales", "total", "sum", "count", "average", "avg",
    "top", "bottom", "highest", "lowest", "best", "worst",
    "by state", "by city", "by category", "by status",
    "how many", "how much", "what is the",
    "distribution", "breakdown", "trend", "growth",
    "compare", "comparison", "percentage", "percent",
    "monthly", "weekly", "daily", "quarterly",
    "this month", "last month", "year",
    "orders", "transactions", "amount", "quantity",
    "cancelled", "shipped", "delivered", "pending",
    "b2b", "merchant", "amazon", "fulfilment",
]

KNOWLEDGE_KEYWORDS = [
    "return", "refund", "exchange", "policy",
    "shipping", "delivery", "ship", "deliver",
    "how long", "how do i", "can i", "what if",
    "size", "sizing", "fit", "measure",
    "care", "wash", "clean", "material", "fabric",
    "quality", "authentic", "guarantee", "warranty",
    "contact", "help", "support", "customer service",
    "track", "tracking", "lost", "damaged", "missing",
    "faq", "question", "guide", "guidelines",
    "eligible", "eligibility", "allowed",
]


def classify_intent(user_query: str) -> dict:
    if not user_query or not user_query.strip():
        return {"intent": "unknown", "confidence": 0.0, "reason": "Empty query"}

    query_lower = user_query.lower()
    logger.info(f"Classifying intent: {user_query[:50]}...")

    analytics_matches = [kw for kw in ANALYTICS_KEYWORDS if kw in query_lower]
    knowledge_matches = [kw for kw in KNOWLEDGE_KEYWORDS if kw in query_lower]

    analytics_score = len(analytics_matches)
    knowledge_score = len(knowledge_matches)

    if analytics_score > knowledge_score:
        intent = "analytics"
        confidence = min(0.9, 0.5 + (analytics_score * 0.1))
        reason = f"Matched analytics keywords: {', '.join(analytics_matches[:5])}"
    elif knowledge_score > analytics_score:
        intent = "knowledge"
        confidence = min(0.9, 0.5 + (knowledge_score * 0.1))
        reason = f"Matched knowledge keywords: {', '.join(knowledge_matches[:5])}"
    elif analytics_score == knowledge_score and analytics_score > 0:
        if re.search(r'\b(how do|can i|what if|where|policy)\b', query_lower):
            intent = "knowledge"
            confidence = 0.6
            reason = "Question pattern suggests knowledge query"
        else:
            intent = "analytics"
            confidence = 0.6
            reason = "Default to analytics for data-related queries"
    else:
        if re.search(r'\b(how much|how many|what is the total|top \d+)\b', query_lower):
            intent = "analytics"
            confidence = 0.7
            reason = "Quantitative question pattern"
        elif re.search(r'\b(how to|how do|can i|what is your|do you)\b', query_lower):
            intent = "knowledge"
            confidence = 0.7
            reason = "Informational question pattern"
        else:
            intent = "analytics"
            confidence = 0.5
            reason = "Default classification"

    logger.info(f"Intent: {intent} (confidence: {confidence:.2f})")

    return {"intent": intent, "confidence": confidence, "reason": reason}
