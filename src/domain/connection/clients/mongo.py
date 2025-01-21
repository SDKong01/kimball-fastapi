from typing import Any
from pymongo import MongoClient
from src.domain.connection.models import ConnClient, ConnParams


class MongoClientConn(ConnClient):
    def __init__(self, conn_params: ConnParams):
        self.conn_params = conn_params

    cache_enabled = False

    params_schema = {
        "host": {"mandatory": True, "type": "str", "beauty_name": "Host"},
        "username": {"mandatory": False, "type": "str", "beauty_name": "Username"},
        "password": {"mandatory": False, "type": "password", "beauty_name": "Password"},
        "port": {
            "mandatory": True,
            "type": "int",
            "defatul": "5432",
            "beauty_name": "Port",
        },
        # "database": {"mandatory": False, "type": "str"},
    }

    query_schema = {
        "database": {"mandatory": True, "type": "str", "beauty_name": "Database"},
        "collection": {"mandatory": True, "type": "str", "beauty_name": "Collection"},
    }

    def stablish_connection(self, **kwargs):
        params = self.conn_params.params
        params["port"] = int(params["port"])
        connection = MongoClient(**params)
        return connection

    def ping(self, connection: Any, *args, **kwargs) -> bool:
        return connection.admin.command('ping')

    def close(self, *args, **kwargs) -> None:
        return None
        self.conn().close()
        return None
