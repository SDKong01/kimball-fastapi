from nest.core import Controller, Depends, Get, Post
from fastapi import UploadFile, File, status, Response, HTTPException
from dataclass_type_validator import TypeValidationError

# local imports
# from src.interface.discovery_engine.serializers import (
#     ConnParamsSerializer,
#     get_conn_params,
#     SchemeParamsSerializer,
#     get_scheme_params,
#     ColumnsParamsSerializer,
#     get_columns_params,
#     EngineParamsSerializer,
# )
from src.application.discovery_engine.services import (
    DiscoveryEngineAppServices,
    # ConnectionDTO,
)

# from src.domain.discovery_engine.models import EngineDTO
# from src.interface.mixins import ErrorResponseSerializer
from src.constants import DB_ENGINES


@Controller(tag="Discovery Engine", prefix="v1/discovery_engine")
class DiscoveryEngineController:
    service: DiscoveryEngineAppServices = Depends(DiscoveryEngineAppServices)

    # @Get(
    #     "/db_schemas",
    #     summary="Get schemas",
    #     description="Get the schemas from the database.",
    #     operation_id="listDbSchemas",
    #     status_code=status.HTTP_200_OK,
    # )
    # async def list_db_schemas(
    #     self, conn_params: ConnParamsSerializer = Depends(get_conn_params)
    # ):
    #     params = ConnectionDTO(**conn_params.dict())
    #     response = self.service.get_schemas(params)
    #     return response

    # @Get(
    #     "/db_tables",
    #     summary="Get tables",
    #     description="Get the tables from the database.",
    #     operation_id="listDbTables",
    #     status_code=status.HTTP_200_OK,
    # )
    # async def list_db_tables(
    #     self, conn_params: SchemeParamsSerializer = Depends(get_scheme_params)
    # ):
    #     params = ConnectionDTO(**conn_params.dict())
    #     response = self.service.get_tables(params)
    #     return response

    # @Get(
    #     "/columns",
    #     summary="Get columns",
    #     description="Get the columns from the database.",
    #     operation_id="listColumns",
    #     status_code=status.HTTP_200_OK,
    # )
    # async def list_columns(
    #     self, conn_params: ColumnsParamsSerializer = Depends(get_columns_params)
    # ):
    #     params = ConnectionDTO(**conn_params.dict())
    #     response = self.service.get_columns(params)
    #     return response

    # @Get(
    #     "/characteristics",
    #     summary="Retrieve the dataset's column characteristics",
    #     description="Retrieve detailed characteristics about the dataset, including granularity, format, and type of columns.",
    #     operation_id="getCharacteristics",
    #     status_code=status.HTTP_200_OK,
    # )
    # async def get_characteristics(
    #     self, conn_params: SchemeParamsSerializer = Depends(get_scheme_params)
    # ):
    #     params = ConnectionDTO(**conn_params.dict())
    #     response = self.service.get_col_characteristics(params)
    #     return response

    # @Get(
    #     "/schema",
    #     summary="Retrieve the schema metadata",
    #     description="Retrieve a list of columns and their corresponding data types from the dataset schema.",
    #     operation_id="getSchema",
    #     status_code=status.HTTP_200_OK,
    # )
    # async def get_schema(
    #     self, conn_params: SchemeParamsSerializer = Depends(get_scheme_params)
    # ):
    #     params = ConnectionDTO(**conn_params.dict())
    #     response = self.service.get_columns(params)
    #     return response

    # @Post(
    #     "/engine",
    #     summary="Configure the discovery engine",
    #     description="Receives the engine configuration parameters from the user form into the backend.",
    #     operation_id="postCharacteristics",
    #     status_code=status.HTTP_200_OK,
    # )
    # async def create_engine(
    #     self,
    #     engine_params: EngineParamsSerializer,
    #     conn_params: SchemeParamsSerializer = Depends(get_scheme_params),
    # ):
    #     _engine = engine_params.dict()
    #     _engine["db_source"] = {
    #         "schema": engine_params.db_source.dbschema,
    #         "table": engine_params.db_source.table,
    #     }
    #     engine_params = EngineDTO(**engine_params.dict())
    #     conn_params = ConnectionDTO(**conn_params.dict())
    #     response = self.service.create_engine(engine_params, conn_params=conn_params)
    #     return response

    @Get(
        "/matrix_exploration",
        summary="Matrix Exploration",
        description="Matrix Exploration",
        operation_id="matrixExploration",
        status_code=status.HTTP_200_OK,
    )
    async def matrix_exploration(self, db: str, coll: str):
        response = self.service.matrix_exploration(db, coll)
        return response
