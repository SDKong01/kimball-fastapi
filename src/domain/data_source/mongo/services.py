from uuid import uuid4
from typing import Dict, Union, List, Type
from src.domain.connection.models import (
    ConnParams,
)

from src.domain.connection.services import ConnServices

from src.domain.data_source.queryset import QuerySet
from src.config import settings


class MongoServices:
    def __init__(self, conn_params: ConnParams):
        self.mongo_manager = ConnServices.get_factory().get_db_manager(conn_params)
        self.our_manager = ConnServices.get_factory().get_db_manager(
            settings.db_client_params
        )
        # self.our_manager = settings.db_client
        self.queryset = QuerySet(db_manager=self.mongo_manager)
        self.our_db = QuerySet(db_manager=self.our_manager)

    def get_repo(self, collection: str, db: str) -> Type[QuerySet]:
        self.queryset.db_manager.collection = collection
        self.queryset.db_manager.db = db
        return self.queryset

    def clone_to_self_db(
        self,
        collection_origin: str,
        db_origin: str,
        collection_dest: str,
        db_dest: str,
        query: Dict[str, Union[str, int]] = None,
    ) -> int:
        # self.our_manager.collection = collection_dest
        # self.our_manager.db = db_dest

        self.queryset.db_manager.collection = collection_origin
        self.queryset.db_manager.db = db_origin
        data = self.queryset.filter(query)

        self.our_manager.collection = collection_dest
        self.our_manager.db = db_dest

        queryset = QuerySet(db_manager=self.our_manager)
        print("intert many", queryset.insert_many(list(data)))
        return len(data)
