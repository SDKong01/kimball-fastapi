from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict, Union
from src.domain.connection.exceptions import MethodNotAvailable
from src.domain.connection.models import DBManager


class QuerySet:
    def __init__(self, db_manager: DBManager, *args, **kwargs):
        self.db_manager = db_manager
        self._result_cache = None
        self._query = {"args": [], "kwargs": {}}

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

    def filter(self, *args, **kwargs):
        clone = self._clone()
        print("clone query", clone._query)
        clone._query["kwargs"] = clone._query["kwargs"] | locals().get("kwargs", {})
        clone._query["args"] = list(clone._query["args"]) + list(
            locals().get("args", [])
        )
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

    def update(self, *args, **kwargs):
        return self.db_manager.update(*args, **kwargs)

    def insert_one(self, *args, **kwargs):
        return self.db_manager.create(*args, **kwargs)

    def insert_many(self, *args, **kwargs):
        return self.db_manager.create(*args, **kwargs)

    # @abstractmethod
    # def as_pd(self, *args, **kwargs):
    #     raise MethodNotAvailable(
    #         method="as_pd",
    #         detail="Method not available for this connection",
    #     )

    def _fetch_all(self, method: str = "all"):
        response = None
        # if self.db_manager.cache_enabled:
        #     response = self._get_persistent_cache()

        response = response or self.db_manager.retrieve(**self._query["kwargs"])

        m = {
            "all": self._all,
            "get": self._get,
            "first": self._first,
            "iterator": self._iterator,
        }

        self._result_cache = m.get(method)(response)

        if self.db_manager.cache_enabled:
            self._set_persistent_cache(self._result_cache)

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
        c = self.__class__(db_manager=self.db_manager)
        c._query = self._query.copy()
        return c
