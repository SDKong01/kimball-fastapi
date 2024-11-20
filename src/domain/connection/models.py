import uuid
from typing import List, Optional, Union, Dict, Any
from abc import ABC, abstractmethod
from dataclass_type_validator import dataclass_validate
from dataclasses import dataclass
from src.constants import DB_ENGINES
from src.domain.connection.exceptions import (
    ConnectionMissinParams,
    MethodNotAvailable,
    ArgumentError,
)


@dataclass_validate
@dataclass(frozen=True)
class ConnectionParams:
    host: str
    username: Optional[str]
    password: Optional[str]


@dataclass_validate
@dataclass(frozen=True)
class StablisConnParams:
    engine: str
    params: Dict[str, str]


@dataclass_validate
@dataclass(frozen=True)
class ConnParams:
    id: Optional[Union[str, uuid.UUID]]
    engine: str
    params: Optional[Dict[str, str]] = None

    def __post_init__(self):
        self.validate_id()
        self.validate_engine()
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

    def validate_engine(self):
        if self.engine not in DB_ENGINES:
            raise ConnectionMissinParams(
                item="engine",
                detail=f"Invalid engine, {self.engine} not supported",
            )

    def validate_params(self):
        if not self.params:
            return
        if not isinstance(self.params, dict):
            raise ConnectionMissinParams(
                item="params",
                detail="Params must be a dictionary",
            )


@dataclass_validate
@dataclass(frozen=True)
class ConnectionEngine:
    id: Union[str, uuid.UUID]
    engine: str
    conn: Any


class BaseConn(ABC):
    def __init__(self, conn_params: ConnParams = None):
        self.conn_params = conn_params
        self.engine = conn_params.engine


class ConnClient(BaseConn):
    @property
    @abstractmethod
    def _schema_required(self) -> bool:
        pass

    @property
    @abstractmethod
    def _db_required(self) -> bool:
        pass

    @property
    @abstractmethod
    def _table_required(self) -> bool:
        pass

    @property
    @abstractmethod
    def _collection_required(self) -> bool:
        pass

    @property
    @abstractmethod
    def cache_enabled(self) -> bool:
        pass

    @property
    @abstractmethod
    def params_schema(self) -> Dict[str, Dict[str, Any]]:
        pass

    def check_conn_params(self):
        if not self.conn_params:
            raise ConnectionMissinParams(
                item="conn_params",
                detail="Connection params are required",
            )
        params = self.conn_params.params
        for key, value in self.params_schema.items():
            mandatory = value.get("mandatory", False)
            if mandatory and key not in params:
                raise ConnectionMissinParams(
                    item=key,
                    detail=f"Missing required param {key}",
                )

    @property
    def schema(self) -> str:
        return ""

    @property
    @abstractmethod
    def db(self) -> str:
        return ""

    @property
    def table(self) -> str:
        return ""

    @property
    @abstractmethod
    def collection(self) -> str:
        return ""

    @schema.setter
    def schema(self, value: str):
        self._schema = value

    def set_extra_params(self, **kwargs):
        self.schema = kwargs.get("schema", "")
        self.db = kwargs.get("db", "")
        self.table = kwargs.get("table", "")
        self.collection = kwargs.get("collection", "")

    def _is_repo_availble(self, raise_exception: bool = False) -> bool:
        return True
        is_all_params: bool = all(
            [
                self._schema_required and self.schema,
                self._db_required and self.db,
                self._table_required and self.table,
                self._collection_required and self.collection,
            ]
        )

        if not is_all_params and raise_exception:
            raise ConnectionMissinParams(
                item=f"{self.conn_params.engine}-params-missing",
                detail="Missing required fields to perform this query",
            )

        return is_all_params

    @abstractmethod
    def conn(**kwargs) -> ConnParams:
        pass

    @abstractmethod
    def is_alive(self, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def ping(self):
        pass

    @abstractmethod
    def close(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def list_databases(self, *args, **kwargs) -> List[str]:
        pass

    @abstractmethod
    def list_collections(self, *args, **kwargs) -> List[str]:
        pass


class DBManager(ConnClient):
    @abstractmethod
    def _create(self, *args):
        raise MethodNotAvailable(
            method="create",
            detail="Method not available for this connection",
        )

    def _args_to_create(self, *args) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        to_insert = args
        if len(to_insert) > 1:
            raise ArgumentError(
                item=f"{self.conn_params.engine}-create-args",
                detail="Only one argument is allowed, use a list wether you need to insert multiple objects",
            )
        return to_insert[0]

    def create(self, *args):
        self._is_repo_availble(raise_exception=True)
        to_insert = self._args_to_create(*args)
        return self._create(to_insert)

    def retrieve(self, **kwargs) -> List[Dict[str, Any]]:
        self._is_repo_availble(raise_exception=True)
        query = self._kwargs_to_query(**kwargs)
        return self._retrieve(*query)

    @abstractmethod
    def _retrieve(self, *args) -> List[Dict[str, Any]]:
        raise MethodNotAvailable(
            method="retrieve",
            detail="Method not available for this connection",
        )

    def update(self, *args, **kwargs):
        query, update = self._kwargs_args_to_update(*args, **kwargs)
        return self._update(query, update)

    # @abstractmethod
    # def _update(self, *args, **kwargs):
    #     raise MethodNotAvailable(
    #         method="update",
    #         detail="Method not available for this connection",
    #     )

    # @abstractmethod
    # def delete(self, *args, **kwargs):
    #     raise MethodNotAvailable(
    #         method="delete",
    #         detail="Method not available for this connection",
    #     )

    @abstractmethod
    def raw_query(self, *args, **kwargs):
        raise MethodNotAvailable(
            method="raw_query",
            detail="Method not available for this connection",
        )

    @abstractmethod
    def _kwargs_to_query(self, **kwargs):
        pass

    # @abstractmethod
    # def _kwargs_args_to_update(self, *args, **kwargs):
    #     pass


class SingleConnFactory(ABC):
    @property
    @abstractmethod
    def instances(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def __new__(cls, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def __delf__(cls) -> None:
        pass
