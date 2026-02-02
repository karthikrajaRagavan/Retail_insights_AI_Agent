import re
import logging
from typing import Optional
from dataclasses import dataclass

from pandasai import Agent
from pandasai.llm.openai import OpenAI

from .connector import DuckDBConnector
from ..duckdb import get_connection
from ...config import OPENAI_API_KEY, OPENAI_MODEL, TABLE_SCHEMAS

logger = logging.getLogger(__name__)


@dataclass
class SQLGenerationResult:
    success: bool
    sql: Optional[str] = None
    error: Optional[str] = None


class SQLGenerator:
    _instance: Optional["SQLGenerator"] = None

    def __init__(self):
        self._agent = None
        self._connectors = []

    @classmethod
    def get_instance(cls) -> "SQLGenerator":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        if self._agent is not None:
            return

        conn = get_connection()

        for table_name, schema in TABLE_SCHEMAS.items():
            if table_name in conn.get_tables():
                connector = DuckDBConnector(
                    conn._conn,
                    table_name,
                    field_descriptions=schema.get("field_descriptions", {})
                )
                self._connectors.append(connector)

        if not self._connectors:
            raise RuntimeError("No tables loaded - cannot initialize SQLGenerator")

        llm = self._create_llm()

        self._agent = Agent(
            self._connectors,
            config={
                "llm": llm,
                "verbose": False,
                "direct_sql": True,
                "enable_cache": False,
            },
        )

        logger.info(f"SQLGenerator initialized with {len(self._connectors)} tables")

    def _create_llm(self) -> OpenAI:
        if OPENAI_MODEL not in OpenAI._supported_chat_models:
            OpenAI._supported_chat_models.append(OPENAI_MODEL)

        llm = OpenAI(api_token=OPENAI_API_KEY, model=OPENAI_MODEL)

        if "4o" in OPENAI_MODEL or "5" in OPENAI_MODEL:
            @property
            def patched_params(self):
                return {"model": self.model, "temperature": self.temperature}
            type(llm)._default_params = patched_params

        return llm

    def generate(self, question: str) -> SQLGenerationResult:
        try:
            self._agent.generate_code(question)
            code = self._agent.last_code_generated
            sql = self._extract_sql(code)

            if sql:
                return SQLGenerationResult(success=True, sql=sql)
            else:
                return SQLGenerationResult(success=False, error="Could not extract SQL from generated code")

        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return SQLGenerationResult(success=False, error=str(e))

    def _extract_sql(self, code: str) -> Optional[str]:
        if not code:
            return None

        patterns = [
            r'(?:sql_query|sql|query)\s*=\s*"""(.+?)"""',
            r'(?:sql_query|sql|query)\s*=\s*"([^"]+)"',
            r"(?:sql_query|sql|query)\s*=\s*'([^']+)'",
            r'execute_sql_query\s*\(\s*"""(.+?)"""\s*\)',
            r'execute_sql_query\s*\(\s*"([^"]+)"\s*\)',
        ]

        for pattern in patterns:
            match = re.search(pattern, code, re.DOTALL)
            if match:
                return match.group(1).strip()

        return None


def get_generator() -> SQLGenerator:
    return SQLGenerator.get_instance()
