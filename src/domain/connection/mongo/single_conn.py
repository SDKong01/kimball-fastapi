from typing import Dict
from pymongo import MongoClient

from src.domain.connection.models import SingleConnFactory, ConnParams


class Connection(SingleConnFactory):

    instances: Dict[str, MongoClient] = {}

    def __new__(cls, conn_params: ConnParams = None):
        if conn_params.id not in cls.instances:
            conn_string = None
            _host: str = conn_params.params.get("host")
            _port: str = conn_params.params.get("port")
            _username: str = conn_params.params.get("username")
            _password: str = conn_params.params.get("password")
            conn_user = f"{_username}" if _username else None
            conn_user = (
                f"{conn_user}:{_password}" if _password and conn_user else conn_user
            )
            conn_string = (
                f"mongodb://{conn_user}@{_host}:{_port}"
                if conn_user
                else f"mongodb://{_host}:{_port}"
            )
            cls.instances[conn_params.id] = MongoClient(conn_string, connect=False)
        return cls.instances[conn_params.id]

    def __del__(self):
        pass
