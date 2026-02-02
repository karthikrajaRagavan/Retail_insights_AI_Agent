import logging

from ..guardrails.nemo import validate_query

logger = logging.getLogger(__name__)


def input_guardrail(user_query: str) -> dict:
    if not user_query or not user_query.strip():
        return {"allowed": False, "message": "Empty query provided", "reason": "No input"}

    logger.info(f"Checking query safety: {user_query[:50]}...")

    try:
        result = validate_query(user_query)
        return {
            "allowed": result.allowed,
            "message": result.message,
            "reason": result.reason,
        }

    except Exception as e:
        logger.error(f"Guardrail check failed: {e}")
        return {
            "allowed": True,
            "message": user_query,
            "reason": f"Guardrail error (fail-open): {str(e)}",
        }
