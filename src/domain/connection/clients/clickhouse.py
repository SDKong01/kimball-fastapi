import clickhouse_connect
from psycopg2 import connect
from psycopg2 import OperationalError
from src.domain.connection.models import ConnClient, ConnParams
from src.domain.connection.exceptions import ConnectionError


class ClickHouseClient(ConnClient):
    def __init__(self, conn_params: ConnParams):
        self.conn_params = conn_params

    cache_enabled = False

    params_schema = {
        "host": {"mandatory": True, "type": "str", "beauty_name": "Host"},
        "username": {"mandatory": True, "type": "str", "beauty_name": "Username"},
        # "password": {"mandatory": True, "type": "password", "beauty_name": "Password"},
        "port": {"mandatory": True, "type": "str", "beauty_name": "Port"},
        "database": {"mandatory": False, "type": "str", "beauty_name": "Database"},
    }

    query_schema = {
        "database": {"mandatory": True, "type": "str", "beauty_name": "Database"},
        # "schema": {"mandatory": True, "type": "str", "beauty_name": "Schema"},
        # "table": {"mandatory": True, "type": "str", "beauty_name": "Table"},
    }

    def stablish_connection(self, **kwargs):
        _params = {**self.conn_params.params}
        try:
            url = f"clickhouse://{_params['host']}:{_params['port']}/{_params['database']}"
            connection = clickhouse_connect.get_client(
                host="34.122.71.71",  # What the hell are you doing here?
                port=_params["port"],
                user=_params["username"],
                database=_params["database"],
            )
        except OperationalError as e:
            raise ConnectionError(
                item="stablish-connection-error",
                detail=f"Error conecting to postgresql",
            )
        except Exception as e:
            raise ConnectionError(
                item="stablish-connection-error",
                detail=f"Error conecting to postgresql",
            )
        return connection

    def ping(self, conn) -> bool:
        return True
        try:
            response = conn.command("SELECT 1")
            return response == [(1,)]
        except Exception:
            return False

    def close(self, conn) -> None:
        conn.close()
        return None

    def _kwargs_args_to_update(self, **kwargs):
        return kwargs

    def to_json(self, query, orient: str = "records", **kwargs):
        only_columns = kwargs.get("available_fields", False)
        print("************************ kwargs **************************")
        print(kwargs)
        parsed_query = self._kwargs_args_to_update(query=query, **kwargs)
        if orient == "records":
            response = self.conn.query(parsed_query)
            column_names = response.column_names
            if only_columns:
                print("************************ columns **************************")
                print(column_names)
                return (str(c) for c in column_names)
                # return list(column_names)
            records = [dict(zip(column_names, row)) for row in response.result_rows]
            return records
        return None
