from typing import Optional, Union, Dict, List
from pydantic import BaseModel


class AllFields(BaseModel):
    username: Optional[str]
    password: Optional[str]
    dsn: Optional[str]
    port: Optional[Union[str, int, None]]
    user: Optional[Union[str, int, None]]
    database: Optional[Union[str, int, None]]
    host: str


class ConnectionParams(BaseModel):
    engine: str
    params: AllFields


class ConnIdParams(BaseModel):
    id: str
    engine: str


class DBRequiredParams(ConnIdParams):
    db: str


class CollectionDBRequiredParams(DBRequiredParams):
    collection: str


class MetadataParams(BaseModel):
    dataset_description: Optional[Dict[str, int]]
    date_column: Optional[str]
    date_grain: Optional[str]
    dataset_name: Optional[str]
    target_columns: Optional[List[str]]
    dataset_type: Optional[str]
    data_source: Dict[str, str]
    default_forecast: Optional[int]
    owner: Optional[str]
    tags: Optional[List[str]]
    description: Optional[str]


class NewDatasetParams(BaseModel):
    connection_id: str
    query_id: str
    query_schema: Optional[str]
    table: Optional[str]
    metadata: MetadataParams
