import logging

from ..database.duckdb import execute_query

logger = logging.getLogger(__name__)


def execute_sql(sql_query: str) -> dict:
    if not sql_query or not sql_query.strip():
        return {
            "status": "error",
            "data": None,
            "columns": None,
            "row_count": 0,
            "message": "Empty query provided",
        }

    logger.info(f"Executing SQL: {sql_query[:50]}...")

    result = execute_query(sql_query)

    if result.success:
        return {
            "status": "success",
            "data": result.data,
            "columns": result.columns,
            "row_count": result.row_count,
            "message": f"Query returned {result.row_count} rows",
        }
    else:
        return {
            "status": "error",
            "data": None,
            "columns": None,
            "row_count": 0,
            "message": result.error,
        }
