from uuid import uuid4
from typing import List, Optional, Dict
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate

from src.domain.data_source.exceptions import (
    DBEngineNotSupported,
)
from src.domain.connection.services import ConnServices
from src.domain.connection.models import ConnParams, ConnectionParams
from src.config import settings


class ConnectionAppServices:
    ### -------------------- DB Connection --------------------
    def get_params_schema(self, engine: str) -> Dict[str, Dict[str, str]]:
        schema = ConnServices.get_client(engine).params_schema
        return schema

    def get_query_schema(self, engine: str) -> Dict[str, Dict[str, str]]:
        schema = ConnServices.get_client(engine).query_schema
        return schema

    def connect_db(self, stablis_conn_params: ConnParams) -> str:
        connector: ConnectionParams = ConnServices.open_persistant_connection(
            stablis_conn_params
        )
        return connector.id

    def connect_test(self, stablis_conn_params: ConnParams) -> str:
        ConnServices.stablish_temporal_conn(stablis_conn_params)
        # try:
        #     ConnServices.stablish_temporal_conn(stablis_conn_params)
        #     return True
        # except Exception as e:
        #     print(e)
        #     return False

    def list_base_schemas(
        self, conn_params: ConnParams, _schema: str, **kwargs
    ) -> List[str]:
        db_manager = ConnServices.get_db_manager(conn_params=conn_params)

        schemas = {
            "databases": db_manager.list_databases,
            "collections": db_manager.list_collections,
            "tables": db_manager.list_tables,
            "schemas": db_manager.list_schemas,
            "suggested_tables": db_manager.list_suggested_tables,
            "views": db_manager.list_views,
            "suggested_views": db_manager.list_suggested_views,
        }

        if _schema not in schemas:
            raise DBEngineNotSupported(
                item="base-schema-search", detail=f"Schema {_schema} not supported"
            )

        return schemas[_schema](**kwargs)

    def change_db(self, conn_params: ConnParams):
        conector = ConnServices.get_existing_connector(conn_params=conn_params)
        params = conector.connection_params

        db = conn_params.params.get("db")
        if not db:
            raise ValueError("DB is required")
        params = {**params}.update({"db": db})
        conector.close()
        connector = self.connect_db(ConnParams(params))
        return connector
