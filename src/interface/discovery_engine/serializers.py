from typing import Optional
from fastapi import Query
from pydantic import BaseModel


class ConnParamsSerializer(BaseModel):
    engine: str
    conn_id: str


class SchemeParamsSerializer(BaseModel):
    engine: str
    conn_id: str
    dbschema: str


class ColumnsParamsSerializer(BaseModel):
    engine: str
    conn_id: str
    dbschema: str
    table: str


class DBSourceSerializer(BaseModel):
    dbschema: str
    table: str


class EngineParamsSerializer(BaseModel):
    engine_name: str
    catalog: str
    output_table_name: str
    output_table_prefix: Optional[str] = None
    db_source: DBSourceSerializer
    data_storage_name: str
    sample_size: Optional[int] = None


async def get_conn_params(
    engine: str = Query(..., description="Database engine"),
    conn_id: str = Query(..., description="Connection ID"),
) -> ConnParamsSerializer:
    return ConnParamsSerializer(
        engine=engine,
        conn_id=conn_id,
    )


async def get_scheme_params(
    engine: str = Query(..., description="Database engine"),
    conn_id: str = Query(..., description="Connection ID"),
    dbschema: str = Query(..., description="Database Schema"),
) -> SchemeParamsSerializer:
    return SchemeParamsSerializer(
        engine=engine,
        conn_id=conn_id,
        dbschema=dbschema,
    )


async def get_columns_params(
    engine: str = Query(..., description="Database engine"),
    conn_id: str = Query(..., description="Connection ID"),
    dbschema: str = Query(..., description="Database Schema"),
    table: str = Query(..., description="Table name"),
) -> ColumnsParamsSerializer:
    return ColumnsParamsSerializer(
        engine=engine,
        conn_id=conn_id,
        dbschema=dbschema,
        table=table,
    )
