from typing import Any, Dict, List
from uuid import uuid4
from bson import ObjectId
from src.infrastructure.mongo_manager.mongo_db_connection import MongoDBConnection
from src.domain.data_source.models import DataSourceFactory, MongoConnector
from src.infrastructure.mongo_manager.bson_abstract_factory import AbstractBSONFactory
from src.infrastructure.pg_manager.pg_connection import PostgresConnection
from src.config import settings


class DataSourceRepo(AbstractBSONFactory):
    def __init__(self, collection: str) -> None:
        self.db = settings.mongo_client[settings.MONGO_DB][collection]

    def _convert_object_id(self, document: Dict[str, Any]) -> Dict[str, Any]:
        if '_id' in document and isinstance(document['_id'], ObjectId):
            document['_id'] = str(document['_id'])
        return document

    def insert_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.insert_one(data)

    def update_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.update_one(data)

    def insert_many(self, data: List[Dict[str, Any]], **kwargs) -> List[Any]:
        result = self.db.insert_many(data)
        return result.inserted_ids

    def find_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.find_one(data)

    def find(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.find(data)


class DataSourceServices:
    @staticmethod
    def get_factory() -> DataSourceFactory:
        return DataSourceFactory

    @staticmethod
    def get_repo(collection: str = None) -> AbstractBSONFactory:
        kwargs = {"collection": collection} if collection else {}
        return DataSourceRepo(**kwargs)

    @staticmethod
    def mongo_connect(conn_string: str) -> MongoDBConnection:
        conn_id = str(uuid4())
        conn = MongoDBConnection(connection_string=conn_string, connection_id=conn_id)
        conn.connect()
        result = conn.runCommand({'ping': 1})
        print(result)
        return conn_id

    @staticmethod
    def mongo_close(conn_id: str) -> None:
        conn = MongoDBConnection(connection_id=conn_id)
        conn.close()
        return None

    @staticmethod
    def pg_connect(conn_string: str) -> None:
        conn_id = str(uuid4())
        conn = PostgresConnection(connection_string=conn_string, connection_id=conn_id)

        return conn_id

    @staticmethod
    def pg_close(conn_id: str) -> None:
        pass
