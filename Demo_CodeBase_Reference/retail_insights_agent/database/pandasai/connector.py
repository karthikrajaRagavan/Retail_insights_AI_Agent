import pandas as pd
from pandasai.connectors.sql import SQLConnector


class DuckDBConnector(SQLConnector):
    _shared_connection_id = "duckdb_memory_shared"

    def __init__(self, connection, table_name: str, field_descriptions: dict = None):
        self._conn = connection
        self._table_name = table_name
        self._connection_id = self._shared_connection_id

        cols = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        self._columns = [{"name": c[1], "type": c[2]} for c in cols]
        self._row_count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        self._cache_interval = 0
        self._head_df = None
        self._logger = None
        self.name = table_name
        self.description = None
        self.custom_head = None
        self.field_descriptions = field_descriptions or {}
        self.connector_relations = None

        self._config = self._create_mock_config(table_name)

    def _create_mock_config(self, table_name: str):
        class MockConfig:
            def __init__(self, table):
                self.table = table
                self.dialect = "duckdb"
                self.driver = None
                self.host = "memory"
                self.port = 0
                self.database = ":memory:"
                self.username = ""
                self.password = ""
                self.connect_args = {}
                self.where = None

        return MockConfig(table_name)

    @property
    def config(self):
        return self._config

    @property
    def rows_count(self):
        return self._row_count

    @property
    def columns_count(self):
        return len(self._columns)

    @property
    def column_hash(self):
        return str(hash(tuple(c["name"] for c in self._columns)))

    @property
    def path(self):
        return f"duckdb://:memory:/{self._table_name}"

    @property
    def pandas_df(self):
        return self._head_df

    @property
    def fallback_name(self):
        return self._table_name

    @property
    def cs_table_name(self):
        return self._table_name

    @property
    def type(self):
        return "sql"

    def head(self, n: int = 5) -> pd.DataFrame:
        df = self._conn.execute(f"SELECT * FROM {self._table_name} LIMIT {n}").fetchdf()
        self._head_df = df
        return df

    def execute(self) -> pd.DataFrame:
        return self._conn.execute(f"SELECT * FROM {self._table_name}").fetchdf()

    def execute_direct_sql_query(self, sql: str) -> pd.DataFrame:
        return self._conn.execute(sql).fetchdf()

    def get_head(self) -> pd.DataFrame:
        return self.head()

    def set_additional_filters(self, filters):
        pass

    def equals(self, other) -> bool:
        if isinstance(other, DuckDBConnector):
            return self._connection_id == other._connection_id
        return False
