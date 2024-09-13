from src.domain.discovery_engine.models import PGDiscovery
from src.infrastructure.pg_manager.pg_connection import PostgresConnection
from src.domain.discovery_engine.models import EngineRepo, EngineFactory
from src.infrastructure.pg_manager.pg_connection import PostgresConnection
from src.config import settings
from src.infrastructure.mongo_manager.bson_abstract_factory import AbstractBSONFactory


class DiscoveryEngineServices:
    @staticmethod
    def get_pg_discovery(conn_id) -> PGDiscovery:
        db_conn = PostgresConnection(connection_id=conn_id)
        return PGDiscovery(db_conn)

    @staticmethod
    def get_engine_repo(collection: str = None) -> AbstractBSONFactory:
        return EngineRepo(collection=collection)

    @staticmethod
    def get_engine_factory() -> EngineFactory:
        return EngineFactory
