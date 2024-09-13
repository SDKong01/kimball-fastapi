from nest.core import Controller, Depends, Get, Post
from fastapi import UploadFile, File, status, Response, HTTPException
from dataclass_type_validator import TypeValidationError

# local imports
from src.interface.data_source.serializers import (
    UploadFileResponseSerializer,
    ConnectionParams,
)
from src.application.data_source.services import DataSourceAppServices, DBParamsDTO
from src.interface.mixins import ErrorResponseSerializer
from src.constants import MONGO, DB_ENGINES
from src.domain.data_source.exceptions import DBEngineNotSupported


@Controller(tag="Data Source", prefix="v1/data_source")
class DataSourceController:
    service: DataSourceAppServices = Depends(DataSourceAppServices)

    @Post(
        "/file_upload",
        summary="Upload a file",
        description="Receives a file from the frontend into the backend in the proper serialized format.",
        operation_id="upload_file",
        status_code=status.HTTP_201_CREATED,
        responses={
            201: {"success": True, "data": {"created": 120}},
            400: {
                "success": False,
                "error": {"item": "file", "message": "Invalid file format"},
            },
        },
    )
    async def upload_file(self, file: UploadFile = File(...)):
        response = self.service.upload_file(file)
        response = UploadFileResponseSerializer(
            success=True, data={"created": response}
        )
        return response

    @Post(
        "/connection_params",
        summary="Connection parameters",
        description="Receives the connection parameters from the frontend into the backend in the proper serialized format.",
        operation_id="connection_params",
        status_code=status.HTTP_200_OK,
        responses={
            200: {"success": True, "data": {"created": 120}},
            400: {
                "success": False,
                "error": {
                    "item": "connection",
                    "detail": "Invalid connection parameters",
                },
            },
        },
    )
    async def connection(self, params: ConnectionParams):
        try:
            params = DBParamsDTO(**params.dict())
            response = self.service.connect_db(params)
            return response
        except DBEngineNotSupported as e:
            response = ErrorResponseSerializer(
                success=False, error={"item": e.item, "detail": e.detail}
            )
            raise HTTPException(
                status_code=status.HTTP_418_IM_A_TEAPOT, detail=response.dict()
            )
        except TypeValidationError as e:
            response = ErrorResponseSerializer(
                success=False, error={"item": "db-connection", "detail": str(e)}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=response.dict()
            )
