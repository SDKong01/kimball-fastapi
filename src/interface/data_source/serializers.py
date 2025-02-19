from typing import List, Any, Union, Dict, Optional
from pydantic import BaseModel
from fastapi import File, UploadFile
from src.interface.mixins import BaseResponseMixin


class DataSourcerSerializer(BaseModel):
    sources: List[str]


class FileResumeSerializer(BaseModel):
    file_name: str
    created: int


class CreatedSerializer(BaseModel):
    created: List[str]


class CreatedProccessedSerializer(BaseModel):
    sheets: List[str]
    tables: List[str]


class UploadFileResponseSerializer(BaseResponseMixin):
    data: CreatedSerializer


class UploadandProcessFileResponseSerializer(BaseResponseMixin):
    data: CreatedProccessedSerializer


class CloneDataSerializer(BaseModel):
    engine: str
    conn_id: str
    collection: Optional[str] = None
    db: Optional[str] = None
