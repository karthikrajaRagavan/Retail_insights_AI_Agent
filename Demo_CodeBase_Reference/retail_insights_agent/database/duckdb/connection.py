import atexit
import logging
from typing import Optional

import duckdb

from ...config import DATA_DIR, TABLE_SCHEMAS

logger = logging.getLogger(__name__)


class DuckDBConnection:
    _instance: Optional["DuckDBConnection"] = None

    def __init__(self):
        self._conn = duckdb.connect(":memory:")
        self._tables_loaded = False
        self._closed = False

    @classmethod
    def get_instance(cls) -> "DuckDBConnection":
        if cls._instance is None:
            print("[DuckDB] Initializing in-memory database...")
            logger.info("Initializing DuckDB in-memory database...")
            cls._instance = cls()
            cls._instance._load_tables()
            atexit.register(cls._instance.close)
        return cls._instance

    def _load_tables(self) -> None:
        if self._tables_loaded:
            return

        print(f"[DuckDB] Loading tables from {DATA_DIR}...")

        for table_name, schema in TABLE_SCHEMAS.items():
            csv_path = DATA_DIR / schema["source_file"]

            if not csv_path.exists():
                print(f"[DuckDB] WARNING: CSV not found: {csv_path}")
                logger.warning(f"CSV not found: {csv_path}")
                continue

            self._load_csv(table_name, csv_path, schema.get("column_mapping", {}))

        self._tables_loaded = True
        tables = self.get_tables()
        print(f"[DuckDB] Loaded {len(tables)} tables: {', '.join(tables)}")
        logger.info(f"DuckDB ready with {len(tables)} tables: {', '.join(tables)}")

    def _load_csv(self, table_name: str, csv_path, column_mapping: dict) -> None:
        path_str = str(csv_path).replace("\\", "/")

        if column_mapping:
            select_cols = ", ".join([
                f'"{orig}" as {new}' for orig, new in column_mapping.items()
            ])
            sql = f"CREATE TABLE {table_name} AS SELECT {select_cols} FROM read_csv_auto('{path_str}')"
        else:
            sql = f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{path_str}')"

        try:
            self._conn.execute(sql)
            count = self._conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"[DuckDB] Loaded {table_name}: {count:,} rows")
            logger.info(f"Loaded {table_name}: {count:,} rows")
        except Exception as e:
            print(f"[DuckDB] ERROR loading {table_name}: {e}")
            logger.error(f"Failed to load {table_name}: {e}")

    def execute(self, sql: str):
        if self._closed:
            raise RuntimeError("DuckDB connection is closed")
        return self._conn.execute(sql)

    def get_tables(self) -> list:
        result = self._conn.execute("SHOW TABLES").fetchall()
        return [row[0] for row in result]

    def get_table_info(self, table_name: str) -> dict:
        cols = self._conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        count = self._conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        return {
            "name": table_name,
            "columns": [{"name": c[1], "type": c[2]} for c in cols],
            "row_count": count,
        }

    def close(self) -> None:
        if not self._closed:
            print("[DuckDB] Closing connection...")
            logger.info("Closing DuckDB connection")
            self._conn.close()
            self._closed = True

    @classmethod
    def reset(cls) -> None:
        if cls._instance:
            cls._instance.close()
        cls._instance = None


def get_connection() -> DuckDBConnection:
    return DuckDBConnection.get_instance()
