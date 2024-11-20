from typing import List, Any, Union, Dict, Optional
from pydantic import BaseModel
from fastapi import File, UploadFile
from src.interface.mixins import BaseResponseMixin


class DataSourcerSerializer(BaseModel):
    sources: List[str]


class ConnectionParams(BaseModel):
    engine: str
    port: str
    host: str
    database: Optional[str]
    username: str
    password: str


class FileResumeSerializer(BaseModel):
    file_name: str
    created: int


class CreatedSerializer(BaseModel):
    created: int


class UploadFileResponseSerializer(BaseResponseMixin):
    data: CreatedSerializer
