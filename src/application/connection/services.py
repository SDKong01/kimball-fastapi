from src.domain.connection.services import ConnServices
from typing import List, Optional
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate
from src.domain.data_source.exceptions import (
    DBEngineNotSupported,
)
from src.constants import DB_ENGINES
from src.domain.connection.services import ConnServices
from src.domain.connection.models import ConnParams, StablisConnParams


class ConnectionAppServices:
    ### -------------------- DB Connection --------------------

    def connect_db(self, stablis_conn_params: StablisConnParams) -> str:
        print("params in connect_db", stablis_conn_params)
        # params.pop("engine")
        conn_id = (
            ConnServices()
            .get_factory()
            .stablish_connection(stablis_conn_params=stablis_conn_params)
        )
        return conn_id

    def list_databases(self, conn_params: ConnParams) -> List[str]:
        print("params in list_databases", conn_params)
        conn = ConnServices().get_factory().get_existing_conn(conn_params=conn_params)
        return conn.list_databases()

    def list_collections(self, conn_params: ConnParams, db: str) -> List[str]:
        conn = ConnServices().get_factory().get_existing_conn(conn_params=conn_params)
        return conn.list_collections(db=db)
