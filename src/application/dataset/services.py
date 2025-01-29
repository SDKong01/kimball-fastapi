from typing import List

from src.domain.dataset.models import Metadata
from src.domain.dataset.services import MetadataServices, DatasetServices
from src.domain.queryset.models import Query
from src.domain.queryset.services import QueryServices
from src.domain.connection.models import ConnParams


class DatasetAppServices:
    def __init__(self):
        pass

    def retrieve(
        self,
        dataset_id: str,
        force_query: bool = False,
    ):
        response = DatasetServices().retrieve_as_queryset(
            dataset_id=dataset_id, force_query=force_query
        )
        return response.to_json()

    def update(
        self,
    ):
        pass

    def delete(
        self,
    ):
        pass

    def create(
        self,
        description: str,
        dataset_name: str,
        conn_params: ConnParams,
        query: Query,
        clone: bool = False,
        tags: List[str] = None,
        default_forecas: int = 6,
    ):
        # print("conn params in aplication", conn_params)
        _query = QueryServices().retrieve(query=query)
        # print("query in aplication", _query)
        response = DatasetServices().create(
            description=description,
            dataset_name=dataset_name,
            conn_params=conn_params,
            query=_query,
            clone=clone,
            tags=tags,
            default_forecas=default_forecas,
        )
        return response


class MetadataAppServices:
    def __init__(self):
        pass

    def retrieve(
        self,
    ):
        pass

    def update(
        self,
    ):
        pass
