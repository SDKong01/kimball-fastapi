import uuid
import pandas as pd
from typing import List, Optional, Union, Dict, Any, Callable
from abc import ABC, abstractmethod
from dataclass_type_validator import dataclass_validate
from dataclasses import dataclass
from src.constants import DB_ENGINES, existing_connections
from src.domain.connection.exceptions import (
    ConnectionMissinParams,
    MethodNotAvailable,
    ArgumentError,
    ConnectionMissing,
)


@dataclass_validate
@dataclass(frozen=False)
class ConnectionParams:
    id: Optional[Union[str, uuid.UUID]]
    engine: str
    connection: Callable
    connection_params: Dict[str, Union[str, int, None]]
    close: Optional[Union[str, None]] = None


@dataclass_validate
@dataclass(frozen=False)
class ConnParams:
    id: Optional[Union[str, uuid.UUID]] = None
    engine: Optional[Union[str, None]] = None
    params: Optional[Dict[str, Union[str, int, None]]] = None

    def __post_init__(self):
        self.validate_id()
        self.validate_params()

    def validate_id(self):
        if not self.id:
            return
        try:
            uuid.UUID(self.id)
        except ValueError:
            raise ConnectionMissinParams(
                item="id",
                detail="Invalid UUID format",
            )

    def validate_params(self):
        if not self.params:
            return
        if self.engine not in DB_ENGINES:
            raise ConnectionMissinParams(
                item="engine",
                detail=f"Invalid engine, {self.engine} not supported",
            )
        if not isinstance(self.params, dict):
            raise ConnectionMissinParams(
                item="params",
                detail="Params must be a dictionary",
            )


class ConnClient:
    def __init__(self, conn_params: ConnParams, *args, **kwargs):
        self.conn_params = conn_params

    @property
    @abstractmethod
    def cache_enabled(self) -> bool:
        pass

    @property
    @abstractmethod
    def params_schema(self) -> Dict[str, Dict[str, Any]]:
        pass

    @property
    @abstractmethod
    def query_schema(self) -> Dict[str, Dict[str, Any]]:
        pass

    @property
    def engine(self) -> str:
        return self.conn_params.engine

    @property
    @abstractmethod
    def collection(self) -> str:
        return ""

    def _conn(self, **kwargs):
        self.check_conn_params()
        return self.conn(**kwargs)

    @abstractmethod
    def stablish_connection(self, **kwargs):
        pass

    def check_conn_params(self, params: Dict[str, Dict[str, Any]]):
        for key, value in self.params_schema.items():
            is_valid = (
                (
                    (not value.get("mandatory", False))
                    or (value.get("mandatory") and params.get(key))
                ),
                (
                    (params.get(key).__class__.__name__ == value.get("type", "str"))
                    or (
                        (
                            params.get(key).__class__.__name__ == "str"
                            and value.get("type", "password")
                        )
                    )
                    or (not value.get("mandatory", False) and not params.get(key))
                ),
            )
            if not all(is_valid):
                raise ConnectionMissinParams(
                    item="conn_params",
                    detail=f"Wrong value for {key} required parameter",
                )

    def _get_connection_by_id(self):
        id = self.conn_params.id
        conn = getattr(existing_connections.get(id, {}), "connection")
        if not conn:
            raise ConnectionMissing(
                item="conn-ping",
                detail=f"Connection with id {self.conn_params.id} not exists. Provide a valid id or conection parameters to create a new connection",
            )
        if not self.ping(conn):
            raise ConnectionMissing(
                item="conn-ping",
                detail="Connection not available. Check your connection parameters",
            )
        return conn

    def _get_connection_by_params(self):
        self.check_conn_params(self.conn_params.params)
        connection = self.stablish_connection()
        if not self.ping(connection):
            raise ConnectionMissing(
                item="conn-ping",
                detail="Connection not available. Check your connection parameters",
            )
        return connection

    def conn(self, save_connection: bool = True, **kwargs) -> Any:
        if self.conn_params.id:
            connection = self._get_connection_by_id()
            if self.ping(connection):
                return connection

        if self.conn_params.params:
            connection = self._get_connection_by_params()
            if not self.ping(connection):
                raise ConnectionMissing(
                    item="conn-ping",
                    detail="Connection not available. Check your connection parameters",
                )

            if save_connection:
                id = (
                    str(uuid.uuid4())
                    if not self.conn_params.id
                    else self.conn_params.id
                )
                connector = ConnectionParams(
                    id=id,
                    engine=self.conn_params.engine,
                    connection=connection,
                    # close=self.close(connection),
                    connection_params=self.conn_params.params,
                )
                self.conn_params.id = id
                existing_connections[id] = connector
            return connection

    @abstractmethod
    def ping(self, connection: Any, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def close(self, *args, **kwargs) -> None:
        pass


class DBManager(ABC):
    def __init__(self, connection: ConnClient, *args, **kwargs):
        self.connection = connection
        self.conn = connection.conn()

    @abstractmethod
    @abstractmethod
    def create(self, query, **kwargs):
        raise MethodNotAvailable(
            method="create",
            detail="Method not available for this connection",
        )

    @abstractmethod
    def retrieve(self, query, **kwargs) -> List[Dict[str, Any]]:
        raise MethodNotAvailable(
            method="retrieve",
            detail="Method not available for this connection",
        )

    def update(self, *args, **kwargs):
        raise MethodNotAvailable(
            method="update",
            detail="Method not available for this connection",
        )

    def delete(self, *args, **kwargs):
        raise MethodNotAvailable(
            method="delete",
            detail="Method not available for this connection",
        )

    @abstractmethod
    def raw_query(self, *args, **kwargs):
        raise MethodNotAvailable(
            method="raw_query",
            detail="Method not available for this connection",
        )

    def list_databases(self, *args, **kwargs) -> List[str]:
        raise MethodNotAvailable(
            method="list_databases",
            detail="Method not available for this connection",
        )

    def list_collections(self, *args, **kwargs) -> List[str]:
        raise MethodNotAvailable(
            method="list_collections",
            detail="Method not available for this connection",
        )

    def list_tables(self, *args, **kwargs) -> List[str]:
        raise MethodNotAvailable(
            method="list_tables",
            detail="Method not available for this connection",
        )

    def list_suggested_tables(self, *args, **kwargs) -> List[str]:
        raise MethodNotAvailable(
            method="list_sugested_tables",
            detail="Method not available for this connection",
        )

    def list_schemas(self, *args, **kwargs) -> List[str]:
        raise MethodNotAvailable(
            method="list_schema",
            detail="Method not available for this connection",
        )

    def list_views(self, *args, **kwargs) -> List[str]:
        raise MethodNotAvailable(
            method="list_views",
            detail="Method not available for this connection",
        )

    def list_suggested_views(self, *args, **kwargs) -> List[str]:
        raise MethodNotAvailable(
            method="list_suggested_views",
            detail="Method not available for this connection",
        )

    def stats(self, *args, **kwargs) -> Dict[str, Any]:
        raise MethodNotAvailable(
            method="stats",
            detail="Method not available for this connection",
        )

    @abstractmethod
    def to_json(self, query, orient: str = "records", **kwargs) -> List[Dict[str, Any]]:
        pass

    def to_pandas(self, query, orient: str = "record", **kwargs) -> pd.DataFrame:
        data = self.to_json(query=query, orient=orient, **kwargs)
        return pd.DataFrame(data, columns=data[0].keys())
