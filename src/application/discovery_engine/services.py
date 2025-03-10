import re
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate
from src.domain.dataset.services import DatasetServices

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

    def matrix_exploration(self, coll: str, has_headers: bool, save: bool = False):
        data_services = DatasetServices()
        data = data_services.retrieve_as_json(coll)[:]
        matrix_explorer = MatrixExplorerTransformations(data)
        response = matrix_explorer.process_matrix(has_headers)
        data_services = DatasetServices()

        if save:
            n = 0
            _response = []
            for r in response:
                col_name = f"temp__{n}"
                data = r.get("data")
                data_services.create_only_data(data=data, collection_name=col_name)
                _response.append(col_name)
                n += 1
                return _response

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

    def _validate_cell_range(self, str):
        excel_regex = r'^[A-Z]{1,3}[1-9][0-9]*:[A-Z]{1,3}[1-9][0-9]*$'
        return bool(re.match(excel_regex, str))

    def _is_raw_data(self, item: Dict[str, Any]) -> bool:
        keys = item.keys()
        if "x" in keys and "y" in keys and "value" in keys:
            return True
        return False

    def excel_exploration(
        self, sheet_name: str, cells_range: str = None, has_headers: bool = True
    ):
        data_services = DatasetServices()
        data = data_services.retrieve_as_json(sheet_name)[:]
        if not self._is_raw_data(data[0]):
            return data
        matrix_explorer = MatrixExplorerTransformations(data)
        if cells_range and not self._validate_cell_range(cells_range):
            raise ("Wrong excel cells range")
        return matrix_explorer.get_raw_data_by_range(
            cell_range=cells_range, has_headers=has_headers
        )

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
    # }>
    # def create_engine(
    #     self, engine_params: EngineDTO, conn_params: ConnectionDTO
    # ) -> EngineDTO:
    #     engine = EngineFactory.build_entity_without_id(engine_dto=engine_params)
    #     db_conn = PostgresConnection(connection_id=conn_params.conn_id)
    #     conn = PGDiscovery(db_conn=db_conn)
    #     engine.save()
    #     engine.create_dataset(conn)
    #     return engine
