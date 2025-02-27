from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class DatasetCreateSerializer(BaseModel):
    description: str
    dataset_name: str
    conn_id: str
    query_id: str
    clone: bool = False
    tags: list = None
    default_forecas: int = 6
    is_self_hosted: bool = False


class DatasetCreateFromTempSerializer(BaseModel):
    description: str
    dataset_name: str
    date_column: str
    temp_dataset_id: str
    tags: list = None


class MetadataResponseSerializer(BaseModel):
    dataset_id: str
    dataset_name: str
    description: str
    created_date: Optional[str] = None
    dimensional_structure: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class MetadataListResponseSerializer(BaseModel):
    dataset_id: str
    dataset_name: str
    description: str
    created_date: Optional[str] = None

    class Config:
        orm_mode = True
