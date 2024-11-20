from uuid import uuid4
from typing import Dict, Union, Any
from src.domain.connection.models import (
    ConnClient,
    ConnParams,
    DBManager,
)

from src.domain.connection.mongo.client import MongoClientConn
from src.constants import MONGO
from src.domain.connection.models import StablisConnParams
from src.domain.connection.mongo.client import MongoManager


class ConnServices:
    @staticmethod
    def get_factory():
        return ConnFactory


# all_params = {MONGO: MongoParams}
engines = {MONGO: MongoManager}


class ConnFactory:

    @staticmethod
    def stablish_connection(stablis_conn_params: StablisConnParams) -> str:
        conn_id = MongoClientConn.stablis_new_conn(**stablis_conn_params.params)
        return conn_id

    @staticmethod
    def close_connection(conn_params: ConnParams) -> None:
        client = engines.get(conn_params.engine, MongoClientConn)(
            conn_params=conn_params
        )
        client.close()
        return None

    @staticmethod
    def get_existing_conn(conn_params: ConnParams):
        engine = engines.get(conn_params.engine, MongoClientConn)
        client = engine(conn_params=conn_params)
        return client

    @staticmethod
    def get_db_manager(conn_params: ConnParams) -> DBManager:
        client = engines.get(conn_params.engine, MongoClientConn)(
            conn_params=conn_params
        )
        return client
