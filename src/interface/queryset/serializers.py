from typing import Optional, Union, Dict, List, Any
from pydantic import BaseModel


class QueryCreateSerializer(BaseModel):
    id: Optional[str] = None
    filters: List[Dict[str, Any]] = None
    exclude: List[Dict[str, Any]] = None
    order_by: str = None
    limit: int = None
    offset: int = None
    headers: Dict[str, Union[str, Dict[str, str], List[str], None]] = None
    fields: List[str] = None
    fields_detail: Dict[str, Union[str, Dict[str, str], List[str], None]] = None
    raw_query: Optional[Union[str, Dict[str, str], List[str], None]] = None
    db: str = None
    collection: str = None
    db_schema: str = None
    table: str = None
    is_cached: bool = True


class QueryResponseSerializer(BaseModel):
    id: Optional[str] = None
    filters: List[Dict[str, Any]] = None
    exclude: List[Dict[str, Any]] = None
    order_by: str = None
    limit: int = None
    offset: int = None
    headers: Dict[str, Union[str, Dict[str, str], List[str], None]] = None
    fields: List[str] = None
    fields_detail: Dict[str, Union[str, Dict[str, str], List[str], None]] = None
    raw_query: Optional[Union[str, Dict[str, str], List[str], None]] = None
    # to_insert: Optional[
    #     Dict[str, Union[str, Dict[str, Union[str, None, int]], List[str], None, int]]
    # ] = None
    db: str = None
    collection: str = None
    db_schema: str = None
    table: str = None


class ConnParamsIDSerializer(BaseModel):
    id: str
