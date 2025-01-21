import re
import uuid
import pandas as pd
from datetime import datetime, timedelta
from dateutil.parser import parse
from typing import List, Dict, Any
from src.domain.connection.models import DBManager, ConnParams
from src.domain.connection.services import ConnServices
from src.domain.queryset.models import Query, Filter
from src.domain.queryset.services import QuerySet
from src.domain.dataset.models import Metadata

from src.domain.discovery_engine.data_transformations.matrix_explorer import (
    MatrixExplorerTransformations,
)

from src.config import settings
from src.constants import EQUAL


class MetadataServices:
    def _compute_date_grain(self, first_date: datetime, second_date: datetime):
        difference = (
            (second_date - first_date).days if first_date and second_date else 2
        )
        date_grain = "dayly"

        if difference < 1:
            date_grain = "hourly"

        if difference >= 1 and difference < 7:
            date_grain = "dayly"

        if difference >= 7 and difference < 30:
            date_grain = "weekly"

        if difference >= 30 and difference < 365:
            date_grain = "monthly"

        return date_grain

    def compute_columns(self, dataset) -> Dict[str, Any]:
        # print("data_types", dataset.dtypes.to_list())
        date_column = None
        dataset_type = "other"
        matrix = MatrixExplorerTransformations(dataset)
        available_columns = list(dataset[0].keys())
        for c in available_columns:
            value = dataset[0].get(c)
            cell_type = matrix.get_value_type(value)
            if cell_type.is_date:
                date_column = c
                dataset_type = "time_series"
                available_columns.remove(c)

        return {
            "date_column": date_column,
            "dataset_type": dataset_type,
            "target_columns": available_columns,
        }

        pass


class DatasetServices:
    @staticmethod
    def system_db_manager() -> DBManager:
        return ConnServices.get_db_manager(conn_params=settings.db_client_params)

    @staticmethod
    def value_as_date(value: str) -> datetime:
        date_pattern = r'\b(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\b'
        if re.match(date_pattern, value):
            try:
                value_date = parse(value, fuzzy=False)
                return value_date
            except:
                pass

    @staticmethod
    def parse_dataset_name(value: str) -> str:
        response = value.replace("_", "").replace(" ", "")
        return response

    def create_only_data(
        self,
        data: dict,
        collection_name: str,
    ) -> Metadata:
        query_save_data = Query(
            db=settings.testing_client,
            collection=collection_name,
            to_insert=data,
        )
        DatasetServices.system_db_manager().create(query_save_data)

    def create(
        self,
        description: str,
        dataset_name: str,
        conn_params: ConnParams,
        query: Query,
        clone: bool = False,
        tags: List[str] = None,
        default_forecas: int = 6,
    ) -> Metadata:
        # print("conn params", conn_params)
        _db_manager = ConnServices.get_db_manager(conn_params)
        queryset = QuerySet(query=query, db_manager=_db_manager)
        data = queryset.limit(1).to_json()
        db_params = ConnServices.get_existing_conn(conn_params=conn_params)
        full_db_params = {
            "params": db_params.connection_params,
            "engine": db_params.engine,
        }
        metadata = Metadata(
            dataset_id=str(uuid.uuid4()),
            dataset_description={
                "rows_count": len(data),
                "columns_count": len(data[0]),
            },
            dataset_name=dataset_name,
            db_params=full_db_params,
            query=query.__dict__,
            owner=settings.testing_client,
            default_forecast=default_forecas,
            is_cloned=clone,
            is_active=True,
            collection_name=DatasetServices.parse_dataset_name(dataset_name),
            date_grain=None,
            date_column=None,
            target_columns=None,
            dataset_type=None,
            data_source=None,
            description=description,
            tags=None,
        )
        if tags:
            metadata.tags = tags

        def remove_bytes_and_lob(obj):
            if isinstance(obj, dict):
                return {k: remove_bytes_and_lob(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [remove_bytes_and_lob(i) for i in obj]
            elif isinstance(obj, bytes):
                return str(obj.decode('utf-8'))
            elif hasattr(obj, 'read') and not isinstance(
                obj, str
            ):  # Check if it's a LOB object
                response = obj.read()
                response = (
                    response.decode('utf-8')
                    if isinstance(response, bytes)
                    else response
                )
                return response
            else:
                return obj

        data = remove_bytes_and_lob(data)

        columns_data = MetadataServices().compute_columns(data)
        for key, value in columns_data.items():
            setattr(metadata, key, value)

        if metadata.dataset_type == "time_series":
            data = queryset.order_by(metadata.date_column).limit(2).to_json()
            first_date = data[0].get(metadata.date_column)
            first_date = DatasetServices.value_as_date(first_date)
            if len(data) > 1:
                second_date = data[1].get(metadata.date_column)
                second_date = DatasetServices.value_as_date(second_date)
                date_grain = MetadataServices()._compute_date_grain(
                    first_date, second_date
                )
                metadata.date_grain = date_grain

        data = QuerySet(query=query, db_manager=_db_manager).to_json()
        data = remove_bytes_and_lob(data)
        df = pd.DataFrame(data)
        df_stats = df.describe().to_dict()
        descriptive_stats = {}
        for key, value in df_stats.items():
            descriptive_stats[key] = {
                "max": value.get("max"),
                "mean": value.get("mean"),
                # "median": 21205813.17,
                "min": value.get("min"),
                "quartile_1": value.get("25%"),
                "quartile_3": value.get("75%"),
                # "skewness": 0.24271197007491002,
                "std": value.get("std"),
                # "kurtosis": -1.6196558791448692
            }
        metadata.stats = {
            "descriptive_stats": descriptive_stats,
        }

        metadata_dict = metadata.__dict__.copy()
        metadata_dict["query"]["filters"] = [
            f.__dict__ for f in metadata_dict["query"]["filters"]
        ]

        query_save_metadata = Query(
            db=settings.testing_client,
            collection="metadata",
            to_insert=metadata_dict,
        )

        response = Metadata(**metadata.__dict__.copy())

        DatasetServices.system_db_manager().create(query_save_metadata)
        # print("df describe", df.describe())
        # print("df describe as dict", df.describe().to_dict())
        # print("data", data.__class__)
        if clone:
            query_save_data = Query(
                db=settings.testing_client,
                collection=metadata.collection_name,
                to_insert=data,
            )
            DatasetServices.system_db_manager().create(query_save_data)
        return response

    @staticmethod
    def retrieve_as_queryset(dataset_id: str, force_query: bool = False) -> QuerySet:

        _filter = Filter(field="dataset_id", operator=EQUAL, value=dataset_id)
        print("db in retrieve", settings.testing_client)
        query = Query(
            db=settings.testing_client,
            collection="metadata",
            filters=[
                _filter,
            ],
        )
        metadata = DatasetServices.system_db_manager().retrieve(query=query)[0]
        print("metadata", metadata)
        metadata = Metadata(**metadata)

        _db_manager = DatasetServices.system_db_manager()

        _query = Query(
            db=settings.testing_client,
            collection=metadata.collection_name,
            filters=[Filter(**f) for f in metadata.query["filters"]],
        )

        if not metadata.is_cloned or force_query:
            _conn_params = ConnParams(**metadata.db_params)
            # Open connection
            _db_manager = ConnServices.open_and_db_manager(conn_params=_conn_params)
            _query = Query(
                **metadata.query,
            )

        response = QuerySet(query=_query, db_manager=_db_manager)

        return response

    @staticmethod
    def retrieve_as_json(dataset_name: str) -> List[Dict[str, Any]]:
        query = Query(
            db=settings.testing_client,
            collection=dataset_name,
        )
        return DatasetServices.system_db_manager().to_json(query=query)

    def update(self):
        pass

    def delete(self):
        pass
