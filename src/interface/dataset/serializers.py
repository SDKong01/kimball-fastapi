from typing import List, Optional, Dict, Any, Optional
from pydantic import BaseModel


class DatasetCreateSerializer(BaseModel):
    description: str
    dataset_name: str
    query_id: str
    is_dim: bool = False
    conn_id: str = None
    clone: bool = False
    tags: list = None
    default_forecas: int = 6
    is_self_hosted: bool = False
    local_dataset_id: str = None
    data_source: Optional[str] = None


class DatasetCreateFromTempSerializer(BaseModel):
    description: str
    dataset_name: str
    date_column: str
    temp_dataset_id: str
    tags: list = None
    has_headers: bool = False
    cells_range: str = None


class MetadataResponseSerializer(BaseModel):
    dataset_id: str
    dataset_name: str
    description: str
    created_date: Optional[str] = None
    dimensional_structure: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    dataset_type: Optional[str] = None
    obt_structure: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True


class MetadataListResponseSerializer(BaseModel):
    dataset_id: str
    dataset_name: str
    description: str
    created_date: Optional[str] = None
    dataset_type: Optional[str] = None

    class Config:
        orm_mode = True
