from redis import Redis
from src.domain.connection.models import ConnClient, ConnParams


class RedisClientConn(ConnClient):
    def __init__(self, conn_params: ConnParams):
        self.conn_params = conn_params

    cache_enabled = False

    params_schema = {
        "host": {"mandatory": True, "type": "str", "beauty_name": "Host"},
        "password": {"mandatory": False, "type": "str", "beauty_name": "Password"},
        "port": {"mandatory": False, "type": "int", "beauty_name": "Port"},
        "db": {"mandatory": False, "type": "int", "beauty_name": "Database"},
    }

    query_schema = {}

    def stablish_connection(self, **kwargs):
        self.connection = Redis(
            **self.conn_params.params,
        )
        return self.connection

    def ping(self, conn) -> bool:
        return bool(conn.ping())

    def close(self) -> None:
        self.conn().close()
        return None
