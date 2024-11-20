from typing import Optional
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate
from src.domain.discovery_engine.models import PGDiscovery
from src.infrastructure.pg_manager.pg_connection import PostgresConnection
from src.domain.discovery_engine.models import EngineRepo, EngineFactory, EngineDTO
from src.domain.discovery_engine.services import DiscoveryEngineServices


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

    def get_schemas(self, conn_params: ConnectionDTO) -> list:
        db_conn = PostgresConnection(connection_id=conn_params.conn_id)
        conn = PGDiscovery(db_conn=db_conn)
        return conn.get_schemas()

    def get_tables(self, conn_params: ConnectionDTO) -> list:
        db_conn = PostgresConnection(connection_id=conn_params.conn_id)
        conn = PGDiscovery(db_conn=db_conn)
        return conn.get_tables_by_shcema(conn_params.dbschema)

    def get_columns(self, conn_params: ConnectionDTO) -> list:
        db_conn = PostgresConnection(connection_id=conn_params.conn_id)
        conn = PGDiscovery(db_conn=db_conn)
        return conn.get_columns_by_table(conn_params.table, conn_params.dbschema)

    {
        "engine": "postgres",
        "port": "5432",
        "host": "localhost",
        "database": "kimballDB",
        "username": "postgres",
        "password": "xCf4nRcFy5fvYOH",
    }

    # TODO - Implement the following method
    def get_col_characteristics(self, conn_params: ConnectionDTO) -> list:
        db_conn = PostgresConnection(connection_id=conn_params.conn_id)
        conn = PGDiscovery(db_conn=db_conn)
        return conn.get_columns_by_table(conn_params.table, conn_params.dbschema)

    def create_engine(
        self, engine_params: EngineDTO, conn_params: ConnectionDTO
    ) -> EngineDTO:
        engine = EngineFactory.build_entity_without_id(engine_dto=engine_params)
        db_conn = PostgresConnection(connection_id=conn_params.conn_id)
        conn = PGDiscovery(db_conn=db_conn)
        engine.save()
        engine.create_dataset(conn)
        return engine
