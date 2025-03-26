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
from src.application.tree.services import TreeAppServices


@Controller(tag="Tree", prefix="v1/tree")
class TreeController:
    service: TreeAppServices = Depends(TreeAppServices)

    @Get(
        "/childs/{node_id}",
        summary="List childs",
        description="List childs.",
        operation_id="list_childs",
    )
    async def list_childs(self, node_id: str):
        response = self.service.list_childs(node_id=node_id)
        return JSONResponse(
            content={"success": True, "result": response}, status_code=201
        )

    @Get(
        "/last_childs/{node_id}",
        summary="List last childs",
        description="List last childs.",
        operation_id="list_last_childs",
    )
    async def list_last_childs(self, node_id: str):
        response = self.service.list_last_childs(node_id=node_id)
        return JSONResponse(
            content={"success": True, "result": response}, status_code=201
        )
