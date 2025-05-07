import json
from typing import List, Dict, Any

import pandas as pd
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
            else DatasetServices.retrive_dim_version(
                dataset_id=dataset_id, force_query=force_query, query_id=query_id
            )
        )
        return response.to_json()

    def get_stats(
        self,
        dataset_id: str,
        query_id: str = None,
    ):
        response = DatasetServices.retrive_dim_version(
            dataset_id=dataset_id, force_query=True, query_id=query_id
        )

        df = pd.DataFrame(response.to_json())
        df_stats = df.describe(include="all").to_dict()

        json_stats = []
        for key, value in df_stats.items():
            if key == "Calendar Date":
                continue
            json_stats.append(
                {
                    "target": key,
                    "mean": value["mean"],
                    "stddev": value["std"],
                    "min": value["min"],
                    "max": value["max"],
                    "unique": int(value["count"]),
                    "missing": int(df[key].isna().sum()),
                }
            )
        # print(json_stats)

        return json_stats

    def get_available_fields(
        self,
        dataset_id: str,
        query_id: str = None,
    ):
        response = DatasetServices.retrive_dim_version(
            dataset_id=dataset_id, query_id=query_id, available_fields=True
        )
        return response.to_json()

    def get_slice_fields(
        self,
        dataset_id: str,
        column_slice: str,
    ):
        response = DatasetServices.get_distinct_values(
            dataset_id=dataset_id, column_name=column_slice
        )
        join_list = [x for x in response.to_json()]
        # print(join_list)
        response_list = list(list(y.values())[0] for y in join_list)
        return response_list
        # return response.to_json()

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
        is_dim: bool = False,
        local_dataset_id: str = None,
        data_source: str = None,
    ):
        # print("conn params in aplication", conn_params)
        if is_dim:
            _query = query
        else:
            _query = QueryServices().retrieve(query=query)
        # print("query in aplication", _query.dimensional_structure)
        response = DatasetServices().create(
            description=description,
            dataset_name=dataset_name,
            data_source=data_source,
            conn_params=conn_params,
            query=_query,
            clone=clone,
            tags=tags,
            default_forecas=default_forecas,
            is_dim=is_dim,
            local_dataset_id=local_dataset_id,
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
        has_headers: bool = False,
        cells_range: str = None,
    ):
        response = DatasetServices().create_from_temp_collection(
            description=description,
            dataset_name=dataset_name,
            date_column=date_column,
            temp_dataset_id=temp_dataset_id,
            # query=query,
            tags=tags,
            has_headers=has_headers,
            cells_range=cells_range,
        )
        return response

    def del_temp_collections(self) -> None:
        collections = DatasetServices.list_temp_collection()
        [DatasetServices.del_collection(collection_name=c) for c in collections]
        return


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


class ForecastAppServices:
    def __init__(self):
        pass

    def create(self, data=List[Dict[str, Any]]) -> None:

        DatasetServices.create_forecast_results(data=data)
        return
