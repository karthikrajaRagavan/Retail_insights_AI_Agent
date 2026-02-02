import logging

from ..database.pandasai import get_generator

logger = logging.getLogger(__name__)


def generate_sql(question: str) -> dict:
    if not question or not question.strip():
        return {"status": "error", "sql": None, "message": "Empty question provided"}

    logger.info(f"Generating SQL for: {question[:50]}...")

    try:
        generator = get_generator()
        result = generator.generate(question)

        if result.success and result.sql:
            return {
                "status": "success",
                "sql": result.sql,
                "message": f"Generated SQL for: {question}",
            }
        else:
            return {
                "status": "error",
                "sql": None,
                "message": result.error or "Failed to generate SQL",
            }

    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        return {"status": "error", "sql": None, "message": str(e)}
