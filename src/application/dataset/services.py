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
        direct_by_collection: bool = False,
        limit: int = None,
        query_id: str = None,
    ):

        response = (
            DatasetServices().retrive_by_collection(dataset_id=dataset_id, limit=limit)
            if direct_by_collection
            else DatasetServices().retrive_dim_version(
                dataset_id=dataset_id, force_query=force_query, query_id=query_id
            )
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

    def create_from_temp_collection(
        self,
        description: str,
        dataset_name: str,
        date_column: str,
        temp_dataset_id: str,
        # query: Query = None,
        tags: List[str] = None,
    ):
        response = DatasetServices().create_from_temp_collection(
            description=description,
            dataset_name=dataset_name,
            date_column=date_column,
            temp_dataset_id=temp_dataset_id,
            # query=query,
            tags=tags,
        )
        return response


class MetadataAppServices:
    def __init__(self):
        pass

    def retrieve(self, dataset_id: str = None) -> Metadata:
        metadata = MetadataServices.retrieve(dataset_id=dataset_id)
        return metadata

    def available_fields(
        self, dataset_id: str = None, query_id: str = None
    ) -> List[str]:
        fields = MetadataServices.available_fields(
            dataset_id=dataset_id, query_id=query_id
        )
        return fields

    def available_groups(
        self, dataset_id: str = None, query_id: str = None
    ) -> List[str]:
        fields = MetadataServices.available_groups(
            dataset_id=dataset_id, query_id=query_id
        )
        return fields

    def update(
        self,
    ):
        pass
