import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict, Union, Type
from src.domain.connection.exceptions import MethodNotAvailable
from src.domain.connection.models import DBManager
from src.domain.connection.services import ConnServices
from src.domain.queryset.models import Query, Filter, DimmensionalStructure

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
from src.config import settings


class QueryServices:
    def __init__(self):
        self.cache_manager = ConnServices.get_db_manager(
            conn_params=settings.cache_client_params
        )

    def create(self, query: Query):
        query_id = query.id or str(uuid.uuid4())
        query.id = query_id
        _query = Filter(
            field=query.id,
            operator=EQUAL,
            value=query.__dict__,
        )
        _query_params = Query(filters=[_query])

        self.cache_manager.create(query=_query_params)
        return query

    def retrieve(self, query: Query) -> Query:
        _query = Filter(
            field="key",
            operator=EQUAL,
            value=query.id,
        )
        _query_params = Query(
            filters=[
                _query,
            ]
        )

        existing_query = self.cache_manager.retrieve(_query_params)[0]
        existing_query = (
            Query(**existing_query)
            if existing_query
            else Query(id=query.id, filters=[])
        )
        existing_query.filters = [Filter(**f) for f in existing_query.filters or []]

        return existing_query

    def update(self, query: Query):
        # query to find existing query
        _query = Filter(
            field="key",
            operator=EQUAL,
            value=query.id,
        )
        # print("_query", _query)
        _query_params = Query(
            filters=[
                _query,
            ]
        )

        existing_query = self.cache_manager.retrieve(_query_params)[0]
        # set existing_query if it exists or an empty Query object
        existing_query = (
            Query(**existing_query)
            if existing_query
            else Query(id=query.id, filters=[])
        )

        # update existing query with new query
        # print("existing_query", existing_query.__dict__)
        # print("new_query", query.__dict__)
        # existing_query.filters = query.filters or []
        # current_filters = existing_query.filters or []
        # current_filters += query.filters if query.filters else []
        # existing_query.filters = current_filters
        # if existing_query.filters and query.filters:
        #     existing_query.filters += query.filters
        for key, value in query.__dict__.items():
            # print("key", key, "value", bool(value))
            # if key == "filters" or not bool(value):
            #     continue

            setattr(existing_query, key, value)

        # create new query in cache
        _query = Filter(
            field=query.id,
            operator=EQUAL,
            value=existing_query.__dict__,
        )
        _query_params = Query(
            filters=[
                _query,
            ]
        )

        self.cache_manager.create(query=_query_params)
        return existing_query

    def update_or_create(self, query: Query):
        query_id = query.id or str(uuid.uuid4())

        # query to find existing query
        _query = Filter(
            field="key",
            operator=EQUAL,
            value=query_id,
        )
        _query_params = Query(filters=[_query])

        existing_query = self.cache_manager.retrieve(_query_params)[0]
        # set existing_query if it exists or an empty Query object
        existing_query = (
            Query(**existing_query) if existing_query else Query(id=query_id, query=[])
        )

        # update existing query with new query
        existing_query.filter += query.filter
        for key, value in query.__dict__.items():
            if key == "filter":
                continue
            setattr(existing_query, key, value)

        # create new query in cache
        _query = Filter(
            field=query.id,
            operator=EQUAL,
            value=existing_query.__dict__,
        )
        _query_params = Query(filters=[_query])
        query = Query(**existing_query.__dict__)

        self.cache_manager.create(query=_query_params)
        return query


class QuerySet:
    def __init__(
        self,
        query: Query,
        db_manager: DBManager,
        is_cached: bool = False,
        dimensional_structure: Dict[str, str] = None,
        *args,
        **kwargs,
    ):
        self.query = query
        self.db_manager = db_manager
        self.is_cached = is_cached

        self._result_cache = None
        self.extra_query_kwargs = kwargs
        self.dimensional_structure = dimensional_structure

    @abstractmethod
    def _set_persistent_cache(self, value):
        pass

    @abstractmethod
    def _get_persistent_cache(self):
        pass

    ########################
    # PYTHON MAGIC METHODS #
    ########################

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)

    def __len__(self):
        return self.count()

    def __bool__(self):
        return self.exists()

    def __getitem__(self, k: int):
        self._fetch_all()
        return self._result_cache[k]

    @abstractmethod
    def _filter(self, *args, **kwargs):
        raise MethodNotAvailable(
            method="filter",
            detail="Method not available for this connection",
        )

    def to_json(self, orient: str = "records", **kwargs) -> List[Dict[str, Any]]:
        if self.is_cached:
            QueryServices().update_or_create(query=self.query, **kwargs)

        _dim_structure = (
            DimmensionalStructure(**self.dimensional_structure)
            if self.dimensional_structure
            else None
        )

        response = self.db_manager.to_json(
            query=self.query,
            orient=orient,
            dim_structure=_dim_structure,
            **kwargs,
        )
        return response

    suffixes = [
        NOT_EQUAL,
        GREATER_THAN,
        GREATER_THAN_EQUAL,
        LESS_THAN,
        LESS_THAN_EQUAL,
        IN,
        NOT_IN,
        LIKE,
        NOT_LIKE,
    ]

    def _args_to_query():
        pass

    def _kwargs_to_query(self, **kwargs) -> List[Filter]:
        suffix = lambda x: str(x).split("_")[-1]
        filter_list = []
        for key, value in kwargs.items():
            if suffix(key) in self.suffixes:
                operation = suffix(key)
                field = key.split("_")[0]
                new_filter = Filter(field=field, operator=operation, value=value)
                filter_list.append(new_filter)

            else:
                new_filter = Filter(field=key, operator=EQUAL, value=value)
                filter_list.append(new_filter)
        return filter_list

    def filter(self, *args, **kwargs):
        clone = self._clone()
        existing_filter_params = clone.query.filter[:]  # copy of existing query params
        new_filter_params = self._kwargs_to_query(**kwargs)
        existing_filter_params += new_filter_params
        clone.query.filter = existing_filter_params

        if self.is_cached:
            QueryServices().update_or_create(query=clone.query)

        return clone

    def all(self):
        return self._clone()

    def get(self, *args, **kwargs):
        clone = self.filter(*args, **kwargs)
        clone._fetch_all(method="get")

        if len(clone._result_cache) > 1:
            raise Exception("Multiple objects returned")

        if not len(clone._result_cache):
            raise Exception("Object not found")

        return clone._result_cache[0]

    def count(self):
        clone = self._clone()
        clone._fetch_all()
        return len(clone._result_cache)

    def exists(self):
        clone = self._clone()
        clone._fetch_all(method="get")
        return bool(clone._result_cache)

    def order_by(self, value: str):
        clone = self._clone()
        clone.query.order_by = value
        return clone

    def limit(self, value: int):
        clone = self._clone()
        clone.query.limit = value
        return clone

    def update(self, *args, **kwargs):
        return self.db_manager.update(*args, **kwargs)

    def insert_one(self, *args, **kwargs):
        return self.db_manager.create(*args, **kwargs)

    def insert_many(self, *args, **kwargs):
        return self.db_manager.create(*args, **kwargs)

    def as_pd(self, orient: str = "records,", *args, **kwargs):
        return self.db_manager.to_pandas(
            query=self.query, orient=orient, *args, **kwargs
        )

    def _fetch_all(self, method: str = "all"):
        response = None
        # if self.db_manager.cache_enabled:
        #     response = self._get_persistent_cache()
        # TODO: should dim structure missing block the query?
        dim_structure = None
        try:
            dim_structure = (
                DimmensionalStructure(**self.dimensional_structure)
                if self.dimensional_structure
                else None
            )
        except Exception as e:
            pass
        response = response or self.db_manager.retrieve(
            self.query, dim_structure=dim_structure
        )

        m = {
            "all": self._all,
            "get": self._get,
            "first": self._first,
            "iterator": self._iterator,
        }

        self._result_cache = m.get(method)(response)

        # if self.db_manager.cache_enabled:
        #     self._set_persistent_cache(self._result_cache)

    def _first(self, response):
        _result_cache = []
        for i in response:
            _result_cache.append(i)
            break
        return _result_cache

    def _get(self, response):
        _result_cache = []
        for i in response:
            _result_cache.append(i)
            if len(_result_cache) > 2:
                break
        return _result_cache

    def _all(self, response):
        return list(response)

    def _iterator(self, response):
        return response

    def _clone(self):
        c = self.__class__(
            query=self.query,
            db_manager=self.db_manager,
            dimensional_structure=self.dimensional_structure,
        )
        query_params = self.query.__dict__.copy()
        c.query = Query(**query_params)
        return c
