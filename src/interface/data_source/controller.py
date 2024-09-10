from nest.core import Controller, Depends, Get, Post
from fastapi import UploadFile, File, status

# local imports
from src.interface.data_source.serializers import (
    UploadFileResponseSerializer,
)
from src.application.data_source.services import DataSourceAppServices
from src.interface.mixins import ErrorResponseSerializer


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
