from typing import Optional
from pydantic import BaseModel


class AllFields(BaseModel):
    username: Optional[str]
    password: Optional[str]
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
