from typing import Dict, Optional, List
import uuid
from pymongo import MongoClient
from src.domain.connection.models import (
    ConnClient,
    ConnectionParams,
    ConnParams,
    SingleConnFactory,
    DBManager,
)

from src.domain.connection.exceptions import ArgumentError


class MongoParams(ConnectionParams):
    db: str
    collection: str
    host: str
    username: Optional[str]
    password: Optional[str]


class Connection(SingleConnFactory):

    instances: Dict[str, MongoClient] = {}

    def __new__(cls, *args, **kwargs):
        instance_id = kwargs.get("id", str(uuid.uuid4()))
        if instance_id not in cls.instances:
            conn_string = None
            _host: str = kwargs.get("host")
            _username: str = kwargs.get("username")
            _password: str = kwargs.get("password")
            conn_user = f"{_username}" if _username else None
            conn_user = (
                f"{conn_user}:{_password}" if _password and conn_user else conn_user
            )
            conn_string = (
                f"mongodb+srv://{conn_user}@{_host}"
                if conn_user
                else f"mongodb://{_host}"
            )
            print
            print("conn_string", conn_string)
            cls.instances[instance_id] = MongoClient(conn_string)
        return cls.instances[instance_id]

    def __del__(self):
        pass


class MongoClientConn(ConnClient):
    def __init__(self, conn_params: ConnParams):
        self.conn_params = conn_params

    _collection_required = True
    _table_required = False
    cache_enabled = False

    params_schema = {
        "host": {"mandatory": True, "type": str},
        "username": {"mandatory": False, "type": str},
        "password": {"mandatory": False, "type": str},
    }

    def is_alive(self):
        return self.ping()

    @property
    def _schema_required(self):
        return True

    @property
    def _db_required(self):
        return True

    @staticmethod
    def stablis_new_conn(*args, **kwargs) -> str:
        instance_id = str(uuid.uuid4())
        Connection(id=instance_id, **kwargs)
        return instance_id

    def conn(self):
        conn_params = self.conn_params.__dict__.copy()
        conn = Connection(**conn_params)
        return conn

    def ping(self):
        return self.conn().runCommand({'ping': 1})
        # return self.conn().ping(*args, **kwargs)

    def close(self) -> None:
        self.conn().close()
        return None

    def list_collections(self, *args, **kwargs) -> List[str]:
        db = kwargs.get("db")
        return list(self.conn()[db].list_collection_names())

    def list_databases(self, *args, **kwargs) -> List[str]:
        return list(self.conn().list_databases())

    collection = ""
    db = ""


class MongoManager(DBManager, MongoClientConn):
    def _create(self, *args):
        to_insert = args[0]

        print("to_insert", to_insert.__class__)

        if isinstance(to_insert, list):
            print("self db", self.db)
            print("self collection", self.collection)
            return self.conn()[self.db][self.collection].insert_many(to_insert)
        if isinstance(to_insert, dict):
            print("self db", self.db)
            print("self collection", self.collection)
            return self.conn()[self.db][self.collection].insert_one(to_insert)

    def _kwargs_to_query(self, **kwargs):
        return kwargs, {"_id": 0}

    def _retrieve(self, *args):
        query = args[0]
        return self.conn()[self.db][self.collection].find(query, {"_id": 0})

    def raw_query(self, query):
        return self.conn()[self.db][self.collection].find(query)
