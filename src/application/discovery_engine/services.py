from typing import Optional
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate

# from src.domain.discovery_engine.models import PGDiscovery
# from src.infrastructure.pg_manager.pg_connection import PostgresConnection
# from src.domain.discovery_engine.models import EngineRepo, EngineFactory, EngineDTO
# from src.domain.discovery_engine.services import DiscoveryEngineServices
from src.domain.discovery_engine.data_transformations.matrix_explorer import (
    MatrixExplorerTransformations,
)

# from src.domain.connection.services import ConnServices
from src.config import settings
from src.domain.dataset.services import DatasetServices


@dataclass_validate
@dataclass(frozen=True)
class ConnectionDTO:
    conn_id: str
    engine: str
    conn_string: Optional[str] = None
    database: Optional[str] = None
    dbschema: Optional[str] = None
    table: Optional[str] = None


class DiscoveryEngineAppServices:
    def __init__(self) -> None:
        pass

    def matrix_exploration(self, db: str, coll: str):
        data_services = DatasetServices()
        data = data_services.retrieve_as_json(db)[:]
        matrix_explorer = MatrixExplorerTransformations(data)
        response = matrix_explorer.process_matrix()
        # print("response", response)
        return response
        # pass
        # our_manager = ConnServices.get_factory().get_db_manager(
        #     settings.db_client_params
        # )
        # queryset = QuerySet(db_manager=our_manager)
        # queryset.db_manager.collection = coll
        # queryset.db_manager.db = db
        # data = queryset.filter({})
        # data = list(data)[:]

    # def get_schemas(self, conn_params: ConnectionDTO) -> list:
    #     db_conn = PostgresConnection(connection_id=conn_params.conn_id)
    #     conn = PGDiscovery(db_conn=db_conn)
    #     return conn.get_schemas()

    # def get_tables(self, conn_params: ConnectionDTO) -> list:
    #     db_conn = PostgresConnection(connection_id=conn_params.conn_id)
    #     conn = PGDiscovery(db_conn=db_conn)
    #     return conn.get_tables_by_shcema(conn_params.dbschema)

    # def get_columns(self, conn_params: ConnectionDTO) -> list:
    #     db_conn = PostgresConnection(connection_id=conn_params.conn_id)
    #     conn = PGDiscovery(db_conn=db_conn)
    #     return conn.get_columns_by_table(conn_params.table, conn_params.dbschema)

    # {
    #     "engine": "postgres",
    #     "port": "5432",
    #     "host": "localhost",
    #     "database": "kimballDB",
    #     "username": "postgres",
    #     "password": "xCf4nRcFy5fvYOH",
    # }

    # # TODO - Implement the following method
    # def get_col_characteristics(self, conn_params: ConnectionDTO) -> list:
    #     db_conn = PostgresConnection(connection_id=conn_params.conn_id)
    #     conn = PGDiscovery(db_conn=db_conn)
    #     return conn.get_columns_by_table(conn_params.table, conn_params.dbschema)

    # def create_engine(
    #     self, engine_params: EngineDTO, conn_params: ConnectionDTO
    # ) -> EngineDTO:
    #     engine = EngineFactory.build_entity_without_id(engine_dto=engine_params)
    #     db_conn = PostgresConnection(connection_id=conn_params.conn_id)
    #     conn = PGDiscovery(db_conn=db_conn)
    #     engine.save()
    #     engine.create_dataset(conn)
    #     return engine
