from typing import List, Dict, Any

from src.domain.connection.models import DBManager
from src.domain.queryset.models import Query
from src.constants import (
    EQUAL,
    NOT_EQUAL,
    GREATER_THAN,
    GREATER_THAN_EQUAL,
    LESS_THAN,
    LESS_THAN_EQUAL,
    IN,
    NOT_IN,
    LIKE,
    NOT_LIKE,
)


class DocumentBasedManager(DBManager):
    def _kwargs_to_query(self, query=Query, **kwargs):
        query_statement = {}
        if not query.filters:
            return query_statement

        for q in query.filters:
            if q.operator == EQUAL:
                query_statement[q.field] = q.value
            elif q.operator == NOT_EQUAL:
                query_statement[q.field] = {"$ne": q.value}
            elif q.operator == GREATER_THAN:
                query_statement[q.field] = {"$gt": q.value}
            elif q.operator == GREATER_THAN_EQUAL:
                query_statement[q.field] = {"$gte": q.value}
            elif q.operator == LESS_THAN:
                query_statement[q.field] = {"$lt": q.value}
            elif q.operator == LESS_THAN_EQUAL:
                query_statement[q.field] = {"$lte": q.value}
            elif q.operator == IN:
                query_statement[q.field] = {"$in": q.value}
            elif q.operator == NOT_IN:
                query_statement[q.field] = {"$nin": q.value}
            elif q.operator == LIKE:
                query_statement[q.field] = {"$regex": q.value}
            elif q.operator == NOT_LIKE:
                query_statement[q.field] = {"$not": {"$regex": q.value}}
            else:
                continue

        return query_statement

    def _kwargs_args_to_update(self, *args, **kwargs):
        db = kwargs.get("db")
        collection = kwargs.get("collection")
        query = args[0]
        update = args[1]

        return (db, collection, query, update)

    def to_json(
        self, query=Query, orient: str = "records", **kwargs
    ) -> List[Dict[str, Any]]:
        db = query.db
        collection = query.collection
        parsed_query = self._kwargs_to_query(query=query, **kwargs)

        response = list(self.conn[db][collection].find(parsed_query, {"_id": 0}))
        return response

    def retrieve(self, query: Query, **kwargs):
        db = query.db
        collection = query.collection
        parsed_query = self._kwargs_to_query(query=query, **kwargs)
        response = list(self.conn[db][collection].find(parsed_query, {"_id": 0}))
        return response

    def create(self, query: Query, **kwargs):
        db = query.db
        collection = query.collection
        query_statement = query.to_insert
        if isinstance(query_statement, dict):
            query_statement = [
                query_statement,
            ]
        # print("query_statement", query_statement)

        self.conn[db][collection].insert_many(query_statement)

    def delete(self, query: Query, **kwargs):
        db = query.db
        collection: str = query.collection

        if collection.startswith("temp_"):
            self.conn[db][collection].drop()
        elif collection.statswith("sys_"):
            raise Exception("Cannot delete system collection")
        else:
            self.conn[db][collection].rename(f"del_{collection}")

    def raw_query(self, *args, **kwargs):
        db = kwargs.get("db")
        collection = kwargs.get("collection")
        # query = args[0]
        response = list(self.conn[db][collection].find(*args))
        return response

    def list_collections(self, *args, **kwargs):
        db = kwargs.get("db")
        prefix = kwargs.get("prefix")
        collections = list(self.conn[db].list_collection_names())
        if prefix:
            collections = [c for c in collections if c.startswith(prefix)]
        return collections

    def list_databases(self, *args, **kwargs) -> List[str]:
        dbs = list(self.conn.list_database_names())
        return dbs

    def update(self, query=Query, *args, **kwargs):
        db = query.db
        if not [kwargs.get("rename_collection")]:
            super().update(*args, **kwargs)
        temp_coll_name = kwargs.get("temp_coll_name")
        new_coll_name = kwargs.get("new_coll_name")

        self.conn[db][temp_coll_name].rename(new_coll_name)
