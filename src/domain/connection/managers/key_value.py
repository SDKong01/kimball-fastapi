import pickle
from typing import List, Dict, Union

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


class KeyValueManager(DBManager):
    KEY_FIELD = "key"

    def retrieve(self, query: Query):
        query_string = None
        for q in query.filters:
            if q.operator == EQUAL and q.field == self.KEY_FIELD:
                query_string = q.value
                break
        result = self.conn.get(query_string)
        result = pickle.loads(result)
        return (result,)

    def create(self, query: Query, **kwargs):
        expire_time = kwargs.get("expire_time", 6000)
        key = None
        value = None
        for q in query.filters:
            # print("q", q)
            if q.operator == EQUAL:
                key = q.field
                value = pickle.dumps(q.value)

        self.conn.set(key, value, expire_time)

    def raw_query(self, query):
        return self.conn.get(query)

    def _kwargs_args_to_update(self, *args, **kwargs):
        return super()._kwargs_args_to_update(*args, **kwargs)

    def to_json(self, query=..., orient="records", **kwargs):
        return super().to_json(query, orient, **kwargs)
