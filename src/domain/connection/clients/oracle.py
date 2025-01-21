from typing import Dict, Optional, List, Type, Any
import cx_Oracle
from src.domain.connection.models import ConnClient, ConnParams
from typing import List, Dict, Any


class OracleClientConn(ConnClient):
    def __init__(self, conn_params: ConnParams):
        self.conn_params = conn_params

    _collection_required = True
    _table_required = False
    cache_enabled = False

    params_schema = {
        "host": {"mandatory": True, "type": "str", "beauty_name": "Host"},
        "user": {"mandatory": False, "type": "str", "beauty_name": "Username"},
        "password": {"mandatory": False, "type": "str", "beauty_name": "Password"},
        "dsn": {"mandatory": True, "type": "str", "beauty_name": "Database"},
        "port": {"mandatory": True, "type": "str", "beauty_name": "Port"},
    }

    query_schema = {
        "database": {"mandatory": True, "type": "str", "beauty_name": "Database"},
        "schema": {"mandatory": True, "type": "str", "beauty_name": "Schema"},
        "table": {"mandatory": True, "type": "str", "beauty_name": "Table"},
    }

    def is_alive(self):
        return self.ping()

    @property
    def _schema_required(self):
        return True

    @property
    def _db_required(self):
        return False

    def stablish_connection(self, **kwargs) -> str:
        dsn = f"{self.conn_params.params.get('host')}:{self.conn_params.params.get('port')}/{self.conn_params.params.get('dsn')}"
        connection = cx_Oracle.connect(
            user=self.conn_params.params.get("user"),
            password=self.conn_params.params.get("password"),
            dsn=dsn,
        )
        return connection

    def ping(self, connection: Any, *args, **kwargs) -> bool:
        return True

    def close(self) -> None:
        self.conn().close()
        return None

    def list_collections(self, *args, **kwargs) -> List[str]:
        return

    def list_databases(self, *args, **kwargs) -> List[str]:
        return

    collection = ""
    db = ""
