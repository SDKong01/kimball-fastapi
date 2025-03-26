from typing import Any, Dict, List, Optional

from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate


# @dataclass_validate
@dataclass(frozen=False)
class Metadata:
    dataset_id: str
    dataset_name: Optional[str]
    dataset_type: Optional[str]
    data_source: Dict[str, str]
    default_forecast: Optional[int]
    owner: Optional[str]
    description: Optional[str]
    is_cloned: Optional[bool]
    collection_name: Optional[str]
    date_grain: Optional[str] = None
    tags: Optional[List[str]] = None
    dataset_description: Optional[Dict[str, int]] = None
    target_columns: Optional[List[str]] = None
    date_column: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = True
    last_run: Optional[str] = None
    query: Optional[Dict[str, Any]] = None
    db_params: Optional[Dict[str, str]] = None
    begin_date: Optional[str] = None
    end_date: Optional[str] = None
    dataset_keywords: Optional[List[str]] = None
    fields_keywords: Optional[Dict[str, List[str]]] = None
    values_keywords: Optional[Dict[str, Any]] = None
    created_date: Optional[str] = None
    dimensional_structure: Optional[Dict[str, Any]] = None
    tree_structure: Optional[Dict[str, Any]] = None
    obt_structure: Optional[Dict[str, Any]] = None
    data_modeling: Optional[str] = None
