from uuid import UUID, uuid4
from dataclass_type_validator import dataclass_validate
from dataclasses import dataclass
from typing import List, Union
from abc import ABC, abstractmethod

from src.domain.data_source.exceptions import InvalidFormatException, InvalidFileType
from src.infrastructure.mongo_manager.mongo_db_connection import MongoDBConnection


@dataclass_validate
@dataclass(frozen=True)
class DataSourceDTO:
    id: Union[str, UUID]
    created_at: str
    updated_at: str

    def __post_init__(self):
        self.validate_id()

    def validate_id(self):
        try:
            UUID(self.id)
        except ValueError:
            raise InvalidFormatException(item="id", detail="Invalid UUID format")


class DataSourceFactory:
    @staticmethod
    def build_entity_without_id(created_at: str, updated_at: str) -> DataSourceDTO:
        id = uuid4()
        return DataSourceDTO(id=id, created_at=created_at, updated_at=updated_at)


class ConnectorDB(ABC):
    @abstractmethod
    def connect(self, *args, **kwargs):
        pass

    @abstractmethod
    def schemas(self, *args, **kwargs) -> List[str]:
        pass

    @abstractmethod
    def tables(self, schema: str = None, *args, **kwargs):
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        pass


class MongoConnector:
    def __init__(self, conn_id: str) -> None:
        self.conn_id = conn_id
        self.db = MongoDBConnection(connection_id=conn_id)

    def collections(self):
        return self.db.list_collections()

    @staticmethod
    def connect(connection_string: str) -> str:
        conn_id = str(uuid4())
        MongoDBConnection(connection_string=connection_string, connection_id=conn_id)
        return conn_id
