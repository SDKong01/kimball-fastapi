from psycopg2 import connect
from psycopg2 import OperationalError
from src.domain.connection.models import ConnClient, ConnParams
from src.domain.connection.exceptions import ConnectionError


class PostgresClientConn(ConnClient):
    def __init__(self, conn_params: ConnParams):
        self.conn_params = conn_params

    cache_enabled = False

    params_schema = {
        "host": {"mandatory": True, "type": "str", "beauty_name": "Host"},
        "user": {"mandatory": True, "type": "str", "beauty_name": "Username"},
        "password": {"mandatory": True, "type": "password", "beauty_name": "Password"},
        "port": {"mandatory": True, "type": "str", "beauty_name": "Port"},
        "database": {"mandatory": False, "type": "str", "beauty_name": "Database"},
    }

    query_schema = {
        "database": {"mandatory": True, "type": "str", "beauty_name": "Database"},
        "schema": {"mandatory": True, "type": "str", "beauty_name": "Schema"},
        "table": {"mandatory": True, "type": "str", "beauty_name": "Table"},
    }

    def stablish_connection(self, **kwargs):
        _params = {**self.conn_params.params}
        try:
            connection = connect(
                **_params,
            )
        except OperationalError as e:
            raise ConnectionError(
                item="stablish-connection-error",
                detail=f"Error conecting to postgresql",
            )
        return connection

    def ping(self, conn) -> bool:
        if conn.closed != 0:
            return False
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                response = cursor.fetchone()
                return bool(response)
        except Exception:
            conn.rollback()
            return False
        return False

    def close(self) -> None:
        self.conn().close()
        return None

    def _kwargs_args_to_update(self, **kwargs):
        return kwargs

    def to_json(self, query, orient: str = "records", **kwargs):
        parsed_query = self._kwargs_to_query(query=query, **kwargs)
        if orient == "records":
            with self.conn.cursor() as cursor:
                cursor.execute(parsed_query)
                column_names = [desc[0] for desc in cursor.description]
                records = [dict(zip(column_names, row)) for row in cursor.fetchall()]

            return records
        return None
