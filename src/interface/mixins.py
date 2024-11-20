from typing import List, Any, Union, Dict, Optional
from pydantic import BaseModel


class BaseResponseMixin(BaseModel):
    success: bool


class PaginationSerializer(BaseResponseMixin):
    next_page_url: str
    page: Optional[int]
    limit: Optional[int]


class ErrorMessageSerializer(BaseModel):
    detail: str
    item: str


class ErrorResponseSerializer(BaseResponseMixin):
    error: ErrorMessageSerializer


class BaseModelFactory:

    def __new__(cls, **kwargs):
        return BaseModel(**kwargs)
