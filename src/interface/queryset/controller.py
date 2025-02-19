from nest.core import Controller, Depends, Get, Post, Patch, Delete
from fastapi import UploadFile, File, status, Response, HTTPException
from fastapi.responses import JSONResponse
from src.application.queryset.services import QuerySetAppServices, HumanQueryDTO
from src.interface.queryset.serializers import (
    QueryCreateSerializer,
    QueryResponseSerializer,
    ConnParamsIDSerializer,
    HumanParseQuery,
)
from src.domain.queryset.models import Query
from src.domain.connection.models import ConnParams


@Controller(tag="QuerySet", prefix="v1/queryset")
class QuerySetController:
    service: QuerySetAppServices = Depends(QuerySetAppServices)

    @Get(
        "/",
        summary="Retrieve queryset",
        description="Retrieve queryset.",
        operation_id="retrieve_queryset",
    )
    async def retrieve(self):
        return self.service.retrieve()

    @Post(
        "/",
        summary="Create queryset",
        description="Create queryset.",
        operation_id="create_queryset",
    )
    async def create(self, query: QueryCreateSerializer):
        _query = Query(
            filters=[],
            db=query.db,
            collection=query.collection,
            table=query.table,
            schema=query.db_schema,
        )
        response = self.service.create(query=_query, is_cached=query.is_cached)
        response = QueryResponseSerializer(**response.__dict__)
        return JSONResponse(content={"success": True, "result": response.dict()})

    @Patch(
        "/",
        summary="Update queryset",
        description="Update queryset.",
        operation_id="update_queryset",
    )
    async def update(self, params: QueryCreateSerializer):
        params_dict = params.dict()
        params_dict["schema"] = params_dict.pop("db_schema")
        params_dict.pop("is_cached")
        query = Query(**params_dict)
        if query.id:
            response = self.service.update(query=query)
        else:
            response = self.service.create(query=query, is_cached=params.is_cached)

        response_dict = response.__dict__
        response_dict["db_schema"] = response_dict.pop("schema")
        response = QueryResponseSerializer(**response.__dict__)
        return JSONResponse(content={"success": True, "result": response.dict()})

    @Get(
        "/run",
        summary="Run queryset",
        description="Run queryset.",
        operation_id="run_queryset",
    )
    async def run_queryset(
        self, query_id: str, conn_id: str = None, is_self_hosted: bool = False
    ):
        conn_params = ConnParams(id=conn_id)
        query = Query(id=query_id)
        if is_self_hosted:
            response = self.service.run_query_self_hosted(query=query, is_cached=False)
        else:
            response = self.service.run_query(
                conn_params=conn_params, query=query, is_cached=False
            )
        return JSONResponse(content={"success": True, "result": response})

    @Get(
        "/date-columns",
        summary="List date columns",
        description="List all the date columns available in the queryset.",
        operation_id="list_date_columns",
    )
    async def list_date_columns(self, conn_id: str, query_id: str):
        conn_params = ConnParams(id=conn_id)
        query = Query(id=query_id)
        response = self.service.list_date_columns(
            conn_params=conn_params, query=query, is_cached=False
        )
        return JSONResponse(content={"success": True, "result": response})

    @Post(
        "/human_query",
        summary="Parse human query",
        description="Parse and save a human query.",
        operation_id="parse_human_query",
    )
    async def human_query(self, params: HumanParseQuery):
        dto = HumanQueryDTO(**params.dict())
        response = self.service.parse_human_query(human_query=dto)
        response = QueryResponseSerializer(**response.__dict__)
        return JSONResponse(content={"success": True, "result": response.dict()})
