import uuid
from typing import List, Optional, Union, Dict, Any, Callable
from abc import ABC, abstractmethod
from dataclass_type_validator import dataclass_validate
from dataclasses import dataclass
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
    value: Union[str, Dict]

    def __post_init__(self):
        self.validate_operator()

    def validate_operator(self):
        if self.operator not in DB_OPERATORS:
            raise ArgumentError(
                item="operator",
                detail=f"Operator {self.operator} not supported",
            )


@dataclass()
class Query:
    id: Optional[str] = None
    filters: List[Filter] = None
    exclude: Optional[List[Filter]] = None
    order_by: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    headers: Optional[Dict[str, Union[str, Dict[str, str], List[str], None]]] = None
    fields: Optional[List[str]] = None
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
