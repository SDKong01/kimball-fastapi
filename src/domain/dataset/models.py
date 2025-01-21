from typing import Any, Dict, List, Optional

from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate


# @dataclass_validate
@dataclass(frozen=False)
class Metadata:
    dataset_id: str
    dataset_description: Optional[Dict[str, int]]
    date_column: Optional[str]
    date_grain: Optional[str]
    dataset_name: Optional[str]
    target_columns: Optional[List[str]]
    dataset_type: Optional[str]
    data_source: Dict[str, str]
    query: Optional[List[Dict[str, str]]]
    db_params: Optional[Dict[str, str]]
    default_forecast: Optional[int]
    owner: Optional[str]
    tags: Optional[List[str]]
    description: Optional[str]
    is_cloned: Optional[bool]
    collection_name: Optional[str]
    stats: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = True
