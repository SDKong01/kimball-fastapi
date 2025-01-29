from nest.core import Controller, Depends, Get, Post
from fastapi import UploadFile, File, status, Response, HTTPException
from fastapi.responses import JSONResponse
from dataclass_type_validator import TypeValidationError

from src.application.dataset.services import DatasetAppServices
from src.interface.dataset.serializers import (
    DatasetCreateSerializer,
)

from src.domain.connection.models import ConnParams
from src.domain.queryset.models import Query


@Controller(tag="Dataset", prefix="v1/dataset")
class DatasetController:
    service: DatasetAppServices = Depends(DatasetAppServices)

    @Post(
        "/create",
        summary="Create dataset",
        description="Create dataset.",
        operation_id="create_dataset",
    )
    async def create(
        self,
        params: DatasetCreateSerializer,
    ):
        response = self.service.create(
            description=params.description,
            dataset_name=params.dataset_name,
            conn_params=ConnParams(id=params.conn_id),
            query=Query(id=params.query_id),
            clone=params.clone,
            tags=params.tags,
            default_forecas=params.default_forecas,
        )
        # print("response", response)
        return JSONResponse(content={"success": True, "result": response.__dict__})

    @Get(
        "/retrieve",
        summary="Retrieve dataset",
        description="Retrieve dataset.",
        operation_id="retrieve_dataset",
    )
    async def retrieve(
        self,
        dataset_id: str,
        force_query: bool = False,
    ):
        response = self.service.retrieve(dataset_id=dataset_id, force_query=force_query)
        return JSONResponse(content={"success": True, "result": response})
