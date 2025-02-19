from typing import List, Dict, Any
from dataclasses import dataclass

from src.domain.queryset.models import Query
from src.domain.connection.models import ConnParams
from src.domain.connection.services import ConnServices
from src.domain.queryset.services import QueryServices, QuerySet
from src.domain.dataset.services import MetadataServices, DatasetServices

from src.config import settings
from src.constants import SYS_METADATA_COLLECTION, DATE_COLUMN_NAME
from src.utils.fuzzy_tools import fuzzy_list_list_match, parse_fields_dict


@dataclass
class HumanQueryDTO:
    dataset_keywords: List[str]
    field_synonyms: Dict[str, List[str]] = None
    value_synonyms: Dict[str, List[str]] = None
    group_by: str = ""
    fields: List[Dict[str, Any]] = None
    filters: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.field_synonyms is None:
            self.field_synonyms = {}
        if self.value_synonyms is None:
            self.value_synonyms = {}
        if self.fields is None:
            self.fields = []


class QuerySetAppServices:
    def _remove_bytes_and_lob(self, obj):
        if isinstance(obj, dict):
            return {k: self._remove_bytes_and_lob(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._remove_bytes_and_lob(i) for i in obj]
        elif isinstance(obj, bytes):
            return str(obj.decode('utf-8'))
        elif hasattr(obj, 'read') and not isinstance(
            obj, str
        ):  # Check if it's a LOB object
            response = obj.read()
            response = (
                response.decode('utf-8') if isinstance(response, bytes) else response
            )
            return response
        else:
            return obj

    def retrieve(self, query: Query):
        response = QueryServices().retrieve(query=query)
        return response

    def create(self, query: Query, is_cached: bool = False) -> Query:
        response = QueryServices().create(query=query)
        return response

    def update(self, query: Query) -> Query:
        response = QueryServices().update(query=query)
        return response

    def delete(self):
        return "QuerysetAppServices.delete"

    def run_query(self, conn_params: ConnParams, query: Query, is_cached: bool):
        result = QueryServices().retrieve(query=query)
        db_manager = ConnServices.get_db_manager(conn_params=conn_params)

        queryset = QuerySet(
            query=result,
            db_manager=db_manager,
            is_cached=is_cached,
        )
        response = queryset.to_json()
        response = self._remove_bytes_and_lob(response)
        return response

    def run_query_self_hosted(self, query: Query, is_cached: bool):
        result = QueryServices().retrieve(query=query)
        db_manager = ConnServices.get_db_manager(conn_params=settings.db_client_params)
        queryset = QuerySet(
            query=result,
            db_manager=db_manager,
            is_cached=is_cached,
        )
        response = queryset.to_json()
        return response

    def list_date_columns(self, conn_params: ConnParams, query: Query, is_cached: bool):
        data = self.run_query(conn_params=conn_params, query=query, is_cached=is_cached)
        columns_data = MetadataServices().compute_columns(data)
        date_column = columns_data.get("date_column")
        if date_column:
            return [
                date_column,
            ]
        return []

    def delete():
        pass

    def parse_human_query(self, human_query: HumanQueryDTO):
        dts_query = DatasetServices.system_db_manager().raw_query(
            {},
            {
                "dataset_id": 1,
                "collection_name": 1,
                "dataset_keywords": 1,
                "fields_keywords": 1,
                "values_keywords": 1,
                "_id": 0,
            },
            db=settings.db_name,
            collection=SYS_METADATA_COLLECTION,
        )
        datasets = list(dts_query)
        score = 0
        metadata = {}
        for dataset in datasets:
            dataset_keywords = dataset.get("dataset_keywords", [])
            human_keywords = human_query.dataset_keywords
            new_score = fuzzy_list_list_match(dataset_keywords, human_keywords)
            if new_score > score:
                score = new_score
                metadata = dataset

        if not metadata:
            return None

        fields_map = parse_fields_dict(
            fields_human=human_query.field_synonyms,
            fields_dataset=metadata.get("fields_keywords", {}),
        )

        parse_field_name = lambda field: (
            DATE_COLUMN_NAME
            if field == DATE_COLUMN_NAME
            else fields_map.get(field, None)
        )

        values_map = parse_fields_dict(
            fields_human=human_query.value_synonyms,
            fields_dataset=metadata.get("value_keywords", {}),
        )

        parse_value_name = lambda field, value: (
            value
            if (field == DATE_COLUMN_NAME or str(value).isdigit())
            else values_map.get(value, value)
        )

        fields = [
            {
                "field": parse_field_name(field.get("field")),
                "operator": field.get("operator", "eq"),
            }
            for field in human_query.fields
        ]

        filters = [
            {
                "field": parse_field_name(f.get("field")),
                "operator": f.get("operator"),
                "value": parse_value_name(f.get("field"), f.get("value")),
            }
            for f in human_query.filters or []
        ]

        query = Query(
            db=settings.testing_client,
            collection=metadata.get("collection_name"),
            filters=filters,
            group_by=parse_field_name(human_query.group_by),
            fields=fields,
        )
        response = QueryServices().create(query=query)
        return response
