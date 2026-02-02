import logging
from typing import Optional
from dataclasses import dataclass, field

from .connection import get_connection

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    success: bool
    data: list = field(default_factory=list)
    columns: list = field(default_factory=list)
    row_count: int = 0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "columns": self.columns,
            "row_count": self.row_count,
            "error": self.error,
        }


def execute_query(sql: str) -> QueryResult:
    if not sql or not sql.strip():
        return QueryResult(success=False, error="Empty SQL query")

    sql_upper = sql.upper().strip()
    if any(sql_upper.startswith(op) for op in ("INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE")):
        return QueryResult(success=False, error="Write operations not permitted")

    try:
        conn = get_connection()
        result_df = conn.execute(sql).fetchdf()

        return QueryResult(
            success=True,
            data=result_df.to_dict(orient="records"),
            columns=list(result_df.columns),
            row_count=len(result_df),
        )

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return QueryResult(success=False, error=str(e))
