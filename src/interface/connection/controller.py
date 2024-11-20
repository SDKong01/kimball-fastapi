from nest.core import Controller, Depends, Get, Post
from fastapi import UploadFile, File, status, Response, HTTPException
from fastapi.responses import JSONResponse
from dataclass_type_validator import TypeValidationError

# local imports
from src.interface.data_source.serializers import (
    UploadFileResponseSerializer,
)
from src.interface.connection.serializers import (
    ConnectionParams,
    ConnIdParams,
    DBRequiredParams,
)
from src.application.data_source.services import DataSourceAppServices
from src.application.connection.services import ConnectionAppServices
from src.interface.mixins import ErrorResponseSerializer
from src.constants import MONGO, DB_ENGINES
from src.domain.data_source.exceptions import DBEngineNotSupported
from src.domain.connection.models import ConnParams, StablisConnParams


@Controller(tag="Connection", prefix="v1/connection")
class ConnectionController:
    service: ConnectionAppServices = Depends(ConnectionAppServices)

    @Post(
        "/connect",
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
            params = StablisConnParams(**params.dict())
            response = self.service.connect_db(params)
            return JSONResponse(
                content={"success": True, "data": {"created": response}}
            )
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

    @Get(
        "/dbs",
        summary="List databases",
        description="List all the databases available in the connection.",
        operation_id="list_databases",
        status_code=status.HTTP_200_OK,
    )
    async def list_databases(self, id: str, engine: str):
        params = ConnParams(
            id=id,
            engine=engine,
            params=None,
        )
        response = self.service.list_databases(params)
        return JSONResponse(content={"success": True, "data": {"databases": response}})

    @Get(
        "/collections",
        summary="List collections",
        description="List all the collections available in the database.",
        operation_id="list_collections",
        status_code=status.HTTP_200_OK,
    )
    async def list_collections(self, id: str, engine, db: str):
        conn_params = ConnParams(id=id, engine=engine, params=None)
        response = self.service.list_collections(conn_params=conn_params, db=db)
        return JSONResponse(
            content={"success": True, "data": {"collections": response}}
        )
