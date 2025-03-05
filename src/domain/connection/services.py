from uuid import uuid4
from typing import Dict, Union, Any
from src.domain.connection.models import (
    ConnClient,
    ConnParams,
    DBManager,
    ConnectionParams,
)

# from src.domain.connection.mongo.client import MongoClientConn
from src.constants import existing_connections, MONGO, ORACLE, POSTGRES, REDIS
from src.domain.connection.clients.oracle import OracleClientConn
from src.domain.connection.managers.sql import SQLManager
from src.domain.connection.managers.dim_sql import SQLManager as DimSQLManager
from src.domain.connection.managers.oracle_sql import OracleManager
from src.domain.connection.clients.postgresql import PostgresClientConn
from src.domain.connection.clients.mongo import MongoClientConn
from src.domain.connection.managers.document_based import DocumentBasedManager
from src.domain.connection.clients.redis import RedisClientConn
from src.domain.connection.managers.key_value import KeyValueManager

from .exceptions import ConnectionError, ConnectionMissinParams

dbmanagers: Dict[str, DBManager] = {
    MONGO: DocumentBasedManager,
    ORACLE: OracleManager,
    POSTGRES: SQLManager,
    REDIS: KeyValueManager,
}
clients: Dict[str, ConnClient] = {
    MONGO: MongoClientConn,
    ORACLE: OracleClientConn,
    POSTGRES: PostgresClientConn,
    REDIS: RedisClientConn,
}


class ConnServices:
    @staticmethod
    def stablish_temporal_conn(conn_params: ConnParams) -> str:
        if not conn_params.engine:
            raise ConnectionMissinParams(
                item="Connectionn", detail="Provide a valid engine"
            )
        client = clients.get(conn_params.engine, MongoClientConn)
        client = client(conn_params=conn_params)
        conn = client.conn(save_connection=False)

        return conn

    @staticmethod
    def open_persistant_connection(conn_params: ConnParams) -> ConnectionParams:
        if not conn_params.engine:
            raise ValueError("Engine is required")
        client = clients.get(conn_params.engine, MongoClientConn)
        client = client(conn_params=conn_params)
        client.conn(save_connection=True)
        connector = existing_connections.get(client.conn_params.id)
        return connector

    @staticmethod
    def get_existing_connection(conn_params: ConnParams):
        conn = existing_connections.get(conn_params.id)
        client = clients.get(conn.engine, MongoClientConn)
        client = client(conn_params=conn.conn_params)
        return client.conn()

    @staticmethod
    def get_existing_connector(conn_params: ConnParams) -> ConnectionParams:
        conn: ConnectionParams = existing_connections.get(conn_params.id)
        return conn

    @staticmethod
    def get_pivot_db_manager(conn_params: ConnParams) -> DBManager:
        client = PostgresClientConn(conn_params=conn_params)
        client.conn(save_connection=True)
        db_manager: DBManager = DimSQLManager(connection=client)
        return db_manager

    @staticmethod
    def open_and_db_manager(conn_params: ConnParams) -> DBManager:
        if not conn_params.engine:
            raise ValueError("Engine is required")
        client = clients.get(conn_params.engine, MongoClientConn)
        client = client(conn_params=conn_params)
        client.conn(save_connection=True)
        connector = existing_connections.get(client.conn_params.id)
        db_manager: DBManager = dbmanagers.get(connector.engine, DocumentBasedManager)(
            connection=client
        )
        return db_manager

    @staticmethod
    def get_db_manager(conn_params: ConnParams) -> DBManager:
        connector = existing_connections.get(conn_params.id)
        client = clients.get(connector.engine, MongoClientConn)(conn_params=conn_params)
        db_manager: DBManager = dbmanagers.get(connector.engine, DocumentBasedManager)(
            connection=client
        )
        return db_manager

    @staticmethod
    def close_connection(conn_params: ConnParams) -> None:
        client = dbmanagers.get(conn_params.engine, MongoClientConn)(
            conn_params=conn_params
        )

        client.close()
        return None

    @staticmethod
    def get_existing_conn(conn_params: ConnParams) -> ConnectionParams:
        if conn_params.id:
            conn: ConnectionParams = existing_connections.get(conn_params.id)
            return conn

        client = clients.get(conn_params.engine, MongoClientConn)
        client = client(conn_params=conn_params)

        return client

    # @staticmethod
    # def get_db_manager(conn_params: ConnParams) -> DBManager:
    #     client = dbmanagers.get(conn_params.engine, MongoClientConn)(
    #         conn_params=conn_params
    #     ).engine
    #     return client

    @staticmethod
    def get_client(engine: str) -> ConnClient:
        client = clients.get(engine, MongoClientConn)
        return client
