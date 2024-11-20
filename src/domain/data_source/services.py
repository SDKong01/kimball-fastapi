from typing import Any, Dict, List
from uuid import uuid4
from starlette.datastructures import UploadFile
from bson import ObjectId
from src.infrastructure.mongo_manager.mongo_db_connection import MongoDBConnection
from src.domain.data_source.models import DataSourceFactory
from src.infrastructure.mongo_manager.bson_abstract_factory import AbstractBSONFactory
from src.infrastructure.pg_manager.pg_connection import PostgresConnection
from src.config import settings
from src.domain.data_source.file_handler.services import FileServices
from src.domain.data_source.mongo.services import MongoServices
from src.constants import MONGO


class DataSourceServices:
    @staticmethod
    def get_factory() -> DataSourceFactory:
        return DataSourceFactory

    @staticmethod
    def file_services() -> FileServices:
        return FileServices()

    @staticmethod
    def mongo_services() -> MongoServices:
        return MongoServices

    # @staticmethod
    # def get_connector_by_engine(engine: str) -> Any:
    #     services = {
    #         MONGO: DataSourceServices.mongo_services,
    #     }
    #     return services.get(engine)
