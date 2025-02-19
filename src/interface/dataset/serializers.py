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
