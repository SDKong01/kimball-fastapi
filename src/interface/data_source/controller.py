from nest.core import Controller, Depends, Get, Post
from fastapi import UploadFile, File, status, HTTPException
from dataclass_type_validator import TypeValidationError

# local imports
from src.interface.data_source.serializers import (
    UploadFileResponseSerializer,
)
from src.application.data_source.services import DataSourceAppServices, CloneParamsDTO
from src.interface.mixins import ErrorResponseSerializer
from src.constants import TEMP_USER_ID
from src.domain.data_source.exceptions import DBEngineNotSupported
from src.interface.data_source.serializers import CloneDataSerializer


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
        response = self.service.upload_file(file=file, db=TEMP_USER_ID)
        response = UploadFileResponseSerializer(
            success=True, data={"created": response}
        )
        return response

    # @Post(
    #     "/clone",
    #     summary="Clone a collection",
    #     description="Clone a collection from one database to another.",
    #     operation_id="clone_collection",
    #     status_code=status.HTTP_201_CREATED,
    # )
    # async def clone(self, params: CloneDataSerializer):
    #     try:
    #         response = self.service.clone(
    #             params=CloneParamsDTO(**params.dict()), db=TEMP_USER_ID
    #         )
    #         response = UploadFileResponseSerializer(
    #             success=True, data={"created": response}
    #         )
    #         return response
    #     except DBEngineNotSupported as e:
    #         response = ErrorResponseSerializer(
    #             success=False, error={"item": e.item, "message": e.detail}
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_418_IM_A_TEAPOT, detail=response.dict()
    #         )
    #     except TypeValidationError as e:
    #         response = ErrorResponseSerializer(
    #             success=False, error={"item": "db-connection", "message": str(e)}
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST, detail=response.dict()
    #         )
