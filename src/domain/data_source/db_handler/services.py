from src.config import settings
from typing import Any, Dict, Union


class DBHandlerServices:
    def __init__(self, conn: str):
        # self.our_db = QuerySet(db_manager=settings.db_client)
        self.our_db = None
        self.conn = conn

    def filter(self, **kwargs):
        pass
        return self.our_db.filter(**kwargs)

    def save_metadata(self, data: dict):
        pass
        # return self.our_db.save(data)

    def clone_to_self_db(
        self,
        collection_dest: str,
        db_dest: str,
        clone: bool = False,
        data: Union[Dict[str, Any], Dict[str, Any], None] = None,
    ):
        pass
        # Save raw data
        # self.our_db.db_manager.collection = collection_dest
        # self.our_db.db_manager.db = db_dest
        # self.our_db.insert_many(data)

        # # Save metadata
        # self.our_db.db_manager.collection = "metadata"
