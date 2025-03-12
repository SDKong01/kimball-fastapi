import uuid
from typing import List, Optional, Union, Dict, Any, Callable
from abc import ABC, abstractmethod
from dataclass_type_validator import dataclass_validate
from dataclasses import dataclass, field
from src.constants import DB_ENGINES, existing_connections, DB_OPERATORS, EQUAL
from src.domain.connection.exceptions import (
    ConnectionMissinParams,
    MethodNotAvailable,
    ArgumentError,
    ConnectionMissing,
)


@dataclass_validate
@dataclass()
class Filter:
    field: str
    operator: str
    value: Union[str, Dict, List[str], None]

    def __post_init__(self):
        self.validate_operator()

    def validate_operator(self):
        return
        if self.operator not in DB_OPERATORS:
            raise ArgumentError(
                item="operator",
                detail=f"Operator {self.operator} not supported",
            )


@dataclass()
class Query:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filters: List[Filter] = field(default_factory=list)
    exclude: Optional[List[Filter]] = None
    order_by: Optional[str] = None
    group_by: Optional[Union[str, List[str]]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    headers: Optional[Dict[str, Union[str, Dict[str, str], List[str], None]]] = None
    fields: Optional[List[Union[str, Filter]]] = None
    fields_detail: Optional[Dict[str, Union[str, Dict[str, str], List[str], None]]] = (
        None
    )
    raw_query: Optional[Union[str, Dict[str, str], List[str], None]] = None
    # to_insert: Optional[
    #     Dict[str, Union[str, Dict[str, Union[str, None, int]], List[str], None, int]]
    # ] = None
    to_insert: Optional[Union[Dict[str, Any], List[Any]]] = None
    db: Optional[str] = None
    collection: Optional[str] = None
    schema: Optional[str] = None
    table: Optional[str] = None
    date_column: Optional[str] = None
    pivot: Optional[str] = None
    pivot_columns: Optional[List[str]] = None


@dataclass()
class PivotColumnsMap:
    column_dim: str
    column_data: str


@dataclass()
class DimmensionalStructure:
    pivot_options: List[str]
    pivot_tables_map: Dict[str, str]
    pivot_columns_map: Dict[str, PivotColumnsMap]
    field_aggregate: str
    fields_raw: List[str]
    table_calendar_dimension: str

    # Check if this fields are required
    pivot_map: Dict[str, str] = field(default_factory=dict)
    group_by_options: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self):
        valid_fields = {f.name for f in self.__dataclass_fields__.values()}
        for key in list(self.__dict__.keys()):
            if key not in valid_fields:
                del self.__dict__[key]
