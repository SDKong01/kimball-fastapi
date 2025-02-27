import re
import uuid
import pandas as pd
from datetime import datetime, timedelta
from dateutil.parser import parse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.domain.connection.models import DBManager, ConnParams
from src.domain.connection.services import ConnServices
from src.domain.queryset.models import Query, Filter, DimmensionalStructure
from src.domain.queryset.services import QuerySet, QueryServices
from src.domain.dataset.models import Metadata
from src.domain.discovery_engine.data_transformations.matrix_explorer import (
    MatrixExplorerTransformations,
)

from src.config import settings
from src.constants import EQUAL, SYS_METADATA_COLLECTION
from src.domain.discovery_engine.data_transformations.matrix_explorer import (
    CellTypeFactory,
)


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
        date_column = None
        dataset_type = "other"
        matrix = MatrixExplorerTransformations(dataset)
        available_columns = list(dataset[0].keys())
        for c in available_columns:
            value = dataset[0].get(c)
            cell_type = CellTypeFactory(value).compute()
            if cell_type.is_date:
                date_column = c
                dataset_type = "time_series"
                available_columns.remove(c)

        return {
            "date_column": date_column,
            "dataset_type": dataset_type,
            "target_columns": available_columns,
        }

    @staticmethod
    def retrieve(dataset_id: str = None) -> List[Metadata]:
        system_db_manager = ConnServices.get_db_manager(
            conn_params=settings.db_client_params
        )
        filters = (
            [Filter(field="dataset_id", operator=EQUAL, value=dataset_id)]
            if dataset_id
            else []
        )
        query = Query(
            db=settings.testing_client,
            collection=SYS_METADATA_COLLECTION,
            filters=filters,
        )
        metadata = system_db_manager.retrieve(query=query)
        metadata = [Metadata(**m) for m in metadata]
        return metadata

    @staticmethod
    def available_fields(dataset_id: str, query_id: str = None) -> QuerySet:
        metadata = MetadataServices.retrieve(dataset_id=dataset_id)[0]

        query_obj = Query(id=query_id)
        query = QueryServices().retrieve(query=query_obj)
        query.schema = metadata.query.get("schema", None)
        query.table = metadata.query.get("table", None)
        query.db = metadata.query.get("db", None)
        query.date_column = metadata.date_column

        _conn_params = ConnParams(**metadata.db_params)
        db_manager = ConnServices.get_pivot_db_manager(conn_params=_conn_params)
        _dim_structure = (
            DimmensionalStructure(**metadata.dimensional_structure)
            if metadata.dimensional_structure
            else None
        )
        fields = getattr(db_manager, "list_fields")(
            query=query, dim_structure=_dim_structure
        )

        return fields

    @staticmethod
    def available_groups(dataset_id: str, query_id: str = None) -> QuerySet:
        metadata = MetadataServices.retrieve(dataset_id=dataset_id)[0]

        query_obj = Query(id=query_id)
        query = QueryServices().retrieve(query=query_obj)
        query.schema = metadata.query.get("schema", None)
        query.table = metadata.query.get("table", None)
        query.db = metadata.query.get("db", None)
        query.date_column = metadata.date_column

        _conn_params = ConnParams(**metadata.db_params)
        db_manager = ConnServices.get_pivot_db_manager(conn_params=_conn_params)
        _dim_structure = (
            DimmensionalStructure(**metadata.dimensional_structure)
            if metadata.dimensional_structure
            else None
        )
        fields = getattr(db_manager, "list_group_by")(dim_structure=_dim_structure)

        return fields


class DatasetServices:
    @staticmethod
    def system_db_manager() -> DBManager:
        return ConnServices.get_db_manager(conn_params=settings.db_client_params)

    @staticmethod
    def value_as_date(value: str) -> datetime:
        date_pattern = r'\b(\d{4}[-/]\d{2}(?:[-/]\d{2})?(?:[T\s]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?)?|\d{2}[-/]\d{2}[-/]\d{4})\b'
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

    @staticmethod
    def retrive_by_collection(dataset_id: str, limit: int = None) -> QuerySet:
        query = Query(
            db=settings.testing_client, collection=dataset_id, filters={}, limit=limit
        )
        response = QuerySet(query=query, db_manager=DatasetServices.system_db_manager())
        return response

    def _rename_collection(self, temp_coll_name: str, new_coll_name: str) -> str:
        query = Query(db=settings.testing_client)
        DatasetServices.system_db_manager().update(
            query=query,
            rename_collection=True,
            temp_coll_name=temp_coll_name,
            new_coll_name=new_coll_name,
        )
        return new_coll_name

    def create_from_temp_collection(
        self,
        description: str,
        dataset_name: str,
        date_column: str,
        temp_dataset_id: str,
        query: Query = None,
        tags: List[str] = None,
    ):
        # TODO: data is stored in memory, change by a lazy function in order to prevent a memory issue
        data = DatasetServices.retrive_by_collection(dataset_id=temp_dataset_id)
        collction_name = self._rename_collection(
            temp_dataset_id, DatasetServices.parse_dataset_name(dataset_name)
        )
        metadata = Metadata(
            dataset_id=str(uuid.uuid4()),
            dataset_description={
                "rows_count": len(data),
                "columns_count": len(data[0]),
            },
            dataset_name=dataset_name,
            db_params=None,
            query=query.__dict__,
            owner=settings.testing_client,
            default_forecast=6,
            is_cloned=True,
            is_active=True,
            collection_name=collction_name,
            date_grain=None,
            date_column=date_column,
            target_columns=None,
            dataset_type=None,
            data_source=None,
            description=description,
            tags=tags,
        )

        columns_data = MetadataServices().compute_columns(data[0])
        for key, value in columns_data.items():
            setattr(metadata, key, value)

        if metadata.dataset_type == "time_series" and len(data) >= 2:
            first_date, second_date = data[0].get(metadata.date_column), data[1].get(
                metadata.date_column
            )
            first_date = DatasetServices.value_as_date(first_date)
            second_date = DatasetServices.value_as_date(second_date)
            date_grain = MetadataServices()._compute_date_grain(first_date, second_date)
            metadata.date_grain = date_grain

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

        query_save_metadata = Query(
            db=settings.db_name,
            collection=SYS_METADATA_COLLECTION,
            to_insert=metadata.__dict__.copy(),
        )

        DatasetServices.system_db_manager().create(query_save_metadata)
        response = Metadata(**metadata.__dict__)
        return response

    def _data(self, queryset: QuerySet):
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

        data = queryset.to_json(replace_date=True)
        data = remove_bytes_and_lob(data)
        return data

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
        _db_manager = ConnServices.get_db_manager(conn_params)
        queryset = QuerySet(query=query, db_manager=_db_manager).limit(1)
        data = self._data(queryset=queryset)

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
            date_column=query.date_column,
            target_columns=None,
            dataset_type=None,
            data_source=None,
            description=description,
            tags=tags,
        )

        columns_data = MetadataServices().compute_columns(data)
        for key, value in columns_data.items():
            setattr(metadata, key, value)

        if metadata.dataset_type == "time_series":
            data = (
                queryset.order_by(metadata.date_column)
                .limit(2)
                .to_json(replace_date=True)
            )
            first_date = data[0].get(metadata.date_column)
            first_date = DatasetServices.value_as_date(first_date)
            if len(data) > 1:
                second_date = data[1].get(metadata.date_column)
                second_date = DatasetServices.value_as_date(second_date)
                date_grain = MetadataServices()._compute_date_grain(
                    first_date, second_date
                )
                metadata.date_grain = date_grain

        queryset.limit(None)
        data = self._data(queryset=queryset)

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
            db=settings.db_name,
            collection=SYS_METADATA_COLLECTION,
            to_insert=metadata_dict,
        )

        response = Metadata(**metadata.__dict__.copy())

        DatasetServices.system_db_manager().create(query_save_metadata)
        if clone:
            query_save_data = Query(
                db=settings.db_name,
                collection=metadata.collection_name,
                to_insert=data,
            )
            DatasetServices.system_db_manager().create(query_save_data)
        return response

    @staticmethod
    def retrive_dim_version(
        dataset_id: str, force_query: bool = False, query_id: str = None
    ) -> QuerySet:
        metadata = MetadataServices.retrieve(dataset_id=dataset_id)[0]

        query_obj = Query(id=query_id)
        query = QueryServices().retrieve(query=query_obj)
        query.schema = metadata.query.get("schema", None)
        query.table = metadata.query.get("table", None)
        query.db = metadata.query.get("db", None)
        query.date_column = metadata.date_column

        _conn_params = ConnParams(**metadata.db_params)
        db_manager = ConnServices.get_pivot_db_manager(conn_params=_conn_params)

        response = QuerySet(
            query=query,
            db_manager=db_manager,
            dimensional_structure=metadata.dimensional_structure,
        )
        return response

    @staticmethod
    def retrieve_as_queryset(dataset_id: str, force_query: bool = False) -> QuerySet:
        metadata = MetadataServices.retrieve(dataset_id=dataset_id)[0]

        _db_manager = DatasetServices.system_db_manager()
        filters = (
            [Filter(**f) for f in metadata.query.get("filters", [])]
            if getattr(metadata, "query", None)
            else []
        )

        _query = Query(
            db=settings.testing_client,
            collection=metadata.collection_name,
            filters=filters,
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
