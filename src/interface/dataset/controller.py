from nest.core import Controller, Depends, Get, Post, Delete
from fastapi import UploadFile, File, status, Response, HTTPException
from fastapi.responses import JSONResponse
from dataclass_type_validator import TypeValidationError

from src.application.dataset.services import DatasetAppServices, MetadataAppServices
from src.interface.dataset.serializers import (
    DatasetCreateSerializer,
    DatasetCreateFromTempSerializer,
    MetadataResponseSerializer,
    MetadataListResponseSerializer,
)

from src.domain.connection.models import ConnParams
from src.domain.queryset.models import Query
from src.config import settings


@Controller(tag="Metadata", prefix="v1/metadata")
class MetadataController:
    service: MetadataAppServices = Depends(MetadataAppServices)

    @Get(
        "/",
        summary="List metadata",
        description="List metadata.",
        operation_id="list_metadata",
    )
    async def list_metadata(self):
        response = self.service.retrieve()
        serialized_response = [
            MetadataListResponseSerializer(**metadata.__dict__).dict()
            for metadata in response
        ]
        return JSONResponse(content={"success": True, "result": serialized_response})

    @Get(
        "/{dataset_id}",
        summary="Retrieve dataset",
        description="Retrieve dataset.",
        operation_id="retrieve_dataset",
    )
    async def retrieve(self, dataset_id: str, fields: str = None):
        response = self.service.retrieve(dataset_id=dataset_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with id {dataset_id} not found",
            )
        serialized_response = MetadataResponseSerializer(**response[0].__dict__).dict()
        if fields:
            fields_list = fields.split(",")
            response = {
                key: serialized_response[key]
                for key in fields_list
                if key in serialized_response
            }
        else:
            response = serialized_response
        return JSONResponse(content={"success": True, "result": response})

    @Get(
        "/{dataset_id}/available_query_fields",
        summary="Retrieve available query fields",
        description="Retrieve available query fields.",
        operation_id="available_query_fields",
    )
    async def available_query_fields(self, dataset_id: str, query_id: str = None):
        response = self.service.available_fields(
            dataset_id=dataset_id, query_id=query_id
        )
        return JSONResponse(content={"success": True, "result": response})

    @Get(
        "/available_groups",
        summary="Retrieve dataset",
        description="Retrieve dataset.",
        operation_id="available_goup_fields",
    )
    async def available_groups(self, dataset_id: str, query_id: str = None):
        response = self.service.available_groups(
            dataset_id=dataset_id, query_id=query_id
        )
        # serialized_response = [
        #     MetadataResponseSerializer(**metadata.__dict__).dict()
        #     for metadata in response
        # ]
        return JSONResponse(content={"success": True, "result": response})


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
        conn_params = (
            settings.db_client_params
            if params.is_self_hosted
            else ConnParams(id=params.conn_id)
        )
        response = self.service.create(
            description=params.description,
            dataset_name=params.dataset_name,
            conn_params=conn_params,
            query=Query(id=params.query_id),
            clone=params.clone,
            tags=params.tags,
            default_forecas=params.default_forecas,
            is_dim=params.is_dim,
            local_dataset_id=params.local_dataset_id,
            data_source=params.data_source,
        )
        # print("response", response)
        return JSONResponse(
            content={"success": True, "result": response.dataset_id},
            status_code=status.HTTP_201_CREATED,
        )

    @Post(
        "/create_from_temp",
        summary="Create dataset from temp",
        description="Create dataset from temp.",
        operation_id="create_dataset_temp",
    )
    async def create_from_temp(
        self,
        params: DatasetCreateFromTempSerializer,
    ):
        response = self.service.create_from_temp_collection(**params.dict())
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
        direct_by_collection: bool = False,
        limit: int = None,
        query_id: str = None,
    ):
        response = self.service.retrieve(
            dataset_id=dataset_id,
            force_query=force_query,
            direct_by_collection=direct_by_collection,
            limit=limit,
            query_id=query_id,
        )
        return JSONResponse(content={"success": True, "result": response})

    @Get(
        "/available_fields",
        summary="Retrieve dataset",
        description="Retrieve dataset.",
        operation_id="available_dataset_fields",
    )
    async def available_fields(
        self,
        dataset_id: str,
        query_id: str = None,
    ):
        response = self.service.get_available_fields(
            dataset_id=dataset_id,
            query_id=query_id,
        )
        return JSONResponse(content={"success": True, "result": response})

    @Get(
        "/slice_fields",
        summary="Retrieve dataset",
        description="Retrieve dataset.",
        operation_id="slice_fields",
    )
    async def slice_fields(
        self,
        dataset_id: str,
        column_slice: str,
    ):
        response = self.service.get_slice_fields(
            dataset_id=dataset_id,
            column_slice=column_slice,
        )
        return JSONResponse(content={"success": True, "result": response})

    @Delete(
        "/temp_collections",
        summary="Delete temp collections",
        description="Delete temp collections.",
        operation_id="delete_temp_collections",
    )
    async def delete_temp_collections(self):
        self.service.del_temp_collections()
        return JSONResponse(content={"success": True})

    @Get(
        "/stats",
        summary="Get dataset stats",
        description="Get dataset stats.",
        operation_id="get_dataset_stats",
    )
    async def get_stats(
        self,
        dataset_id: str,
        query_id: str = None,
    ):
        response = self.service.get_stats(
            dataset_id=dataset_id,
            query_id=query_id,
        )
        return JSONResponse(content={"success": True, "result": response})
