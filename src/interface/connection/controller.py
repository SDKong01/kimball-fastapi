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
)
from src.application.connection.services import (
    ConnectionAppServices,
)
from src.interface.mixins import ErrorResponseSerializer
from src.constants import MONGO, DB_ENGINES, APPLICATION_ENGINES
from src.domain.data_source.exceptions import DBEngineNotSupported
from src.domain.connection.models import ConnParams
from .serializers import EngineAvailables


@Controller(tag="Connection", prefix="v1/connection")
class ConnectionController:
    service: ConnectionAppServices = Depends(ConnectionAppServices)

    @Get(
        "/engines",
        summary="Get available engines",
        description="Returns the available engines for the connection.",
        operation_id="connection_available_engines",
        status_code=status.HTTP_200_OK,
        responses={
            200: {"success": True, "data": {"engines": ["db1", "db2"]}},
        },
    )
    async def available_engines(self):
        serializer = EngineAvailables(
            dbs=DB_ENGINES,
            apps=APPLICATION_ENGINES,
        )
        return JSONResponse(content={"success": True, "data": serializer.dict()})

    @Get(
        "/schema/{engine}",
        summary="Connection parameters schema",
        description="Returns the schema for the connection parameters.",
        operation_id="connection_params_schema",
        status_code=status.HTTP_200_OK,
    )
    async def connection_params_schema(self, engine: str):
        if engine not in DB_ENGINES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {"item": "engine", "detail": "Invalid engine"},
                },
            )
        response = self.service.get_params_schema(engine)
        return JSONResponse(content={"success": True, "data": response})

    @Get(
        "/query-schema/{engine}",
        summary="Connection query parameters schema",
        description="Return the schema with the required fields to run a query.",
        operation_id="connection_query_schema",
        status_code=status.HTTP_200_OK,
    )
    async def connection_query_schema(self, engine: str):
        if engine not in DB_ENGINES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {"item": "engine", "detail": "Invalid engine"},
                },
            )
        response = self.service.get_query_schema(engine)
        return JSONResponse(content={"success": True, "data": response})

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
            dict_params = params.params.dict()
            _params = ConnParams(engine=params.engine, params=dict_params)
            response = self.service.connect_db(_params)
            return JSONResponse(
                content={"success": True, "data": {"connection_id": response}}
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

    @Post(
        "/connection-test",
        summary="Test connection",
        description="Receives the connection parameters from the frontend into the backend in the proper serialized format.",
        operation_id="connection_test",
        status_code=status.HTTP_200_OK,
        responses={
            200: {"success": True, "data": {True}},
            400: {
                "success": False,
                "error": {
                    "item": "connection",
                    "detail": "Invalid connection parameters",
                },
            },
        },
    )
    async def connection_test(self, params: ConnectionParams):
        try:
            dict_params = params.params.dict()
            _params = ConnParams(engine=params.engine, params=dict_params)
            response = self.service.connect_test(_params)
            return JSONResponse(content={"success": True, "data": {response}})
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
    async def list_databases(self, connection_id: str):
        params = ConnParams(id=connection_id)
        response = self.service.list_base_schemas(
            conn_params=params, _schema="databases"
        )
        return JSONResponse(content={"success": True, "data": {"databases": response}})

    @Get(
        "/collections",
        summary="List collections",
        description="List all the collections available in the database.",
        operation_id="list_collections",
        status_code=status.HTTP_200_OK,
    )
    async def list_collections(self, connection_id: str, db: str):
        params = ConnParams(id=connection_id)
        response = self.service.list_base_schemas(
            conn_params=params, _schema="collections", db=db
        )
        return JSONResponse(
            content={"success": True, "data": {"collections": response}}
        )

    @Get(
        "/tables",
        summary="List tables",
        description="List all the tables available in the database.",
        operation_id="list_tables",
        status_code=status.HTTP_200_OK,
    )
    async def list_table(self, connection_id: str, schema: str = None):
        params = ConnParams(id=connection_id)
        response = self.service.list_base_schemas(
            conn_params=params, _schema="tables", schema=schema
        )
        return JSONResponse(content={"success": True, "data": response})

    @Get(
        "/suggest_tables",
        summary="Suggest tables",
        description="Suggest tables available in the database.",
        operation_id="suggest_tables",
        status_code=status.HTTP_200_OK,
    )
    async def suggest_tables(self, connection_id: str):
        params = ConnParams(id=connection_id)
        response = self.service.list_base_schemas(
            conn_params=params, _schema="suggested_tables"
        )
        return JSONResponse(content={"success": True, "data": response})

    @Get(
        "/schemas",
        summary="List schemas",
        description="List all the schemas available in the database.",
        operation_id="list_schemas",
        status_code=status.HTTP_200_OK,
    )
    async def list_schemas(self, connection_id: str):
        params = ConnParams(id=connection_id)
        response = self.service.list_base_schemas(conn_params=params, _schema="schemas")
        return JSONResponse(content={"success": True, "data": response})

    @Get(
        "/views",
        summary="List views",
        description="List all the views available in the database.",
        operation_id="list_views",
        status_code=status.HTTP_200_OK,
    )
    async def list_views(self, connection_id: str):
        params = ConnParams(id=connection_id)
        response = self.service.list_base_schemas(conn_params=params, _schema="views")
        return JSONResponse(content={"success": True, "data": response})

    @Get(
        "/suggest_views",
        summary="Suggest views",
        description="Suggest views available in the database.",
        operation_id="suggest_views",
        status_code=status.HTTP_200_OK,
    )
    async def suggest_views(self, connection_id: str):
        params = ConnParams(id=connection_id)
        response = self.service.list_base_schemas(
            conn_params=params, _schema="suggested_views"
        )
        return JSONResponse(content={"success": True, "data": response})
