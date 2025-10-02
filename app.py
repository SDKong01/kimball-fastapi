import uuid
from os import getenv
from os import environ
from nest.core.app import App
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.mongo_manager.mongo_db_connection import MongoDBConnection

from src.interface.data_source.module import DataSourceModule

from src.interface.discovery_engine.module import DiscoveryEngineModule
from src.interface.connection.module import ConnectionModule
from src.interface.queryset.module import QuerySetModule
from src.interface.dataset.module import DatasetModule
from src.interface.tree.module import TreeModule

from src.domain.connection.models import ConnParams

from src.domain.connection.services import ConnServices
from src.config import settings
import logging


logging.basicConfig(level=logging.INFO)
# logging.getLogger("pymongo").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: App):
    try:
        # Stablis connection to app db
        db_params = ConnParams(
            engine="mongodb",
            params={
                "host": settings.MONGO_HOST,
                "username": settings.MONGO_USER,
                "password": settings.MONGO_PASS,
                "port": settings.MONGO_PORT,
                "is_atlas_cluster": settings.MONGO_IS_ATLAS_CLUSTER,
                # "database": settings.MONGO_DB,
            },
        )
        connector = ConnServices.open_persistant_connection(db_params)
        settings.db_client_connector = connector
        settings.db_client_params = ConnParams(
            id=connector.id, engine=db_params.engine, params=db_params.params
        )
        print("✅ MongoDB connection established")
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        settings.db_client_connector = None
        settings.db_client_params = None

    try:
        # Stablis connection to cache db
        cache_params = ConnParams(
            engine="redis",
            params={
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "password": settings.REDIS_PASS,
                "db": settings.REDIS_DB,
            },
        )
        cache_connector = ConnServices.open_persistant_connection(cache_params)
        settings.cache_client_connector = cache_connector
        settings.cache_client_params = ConnParams(
            id=cache_connector.id, engine=cache_params.engine, params=cache_params.params
        )
        print("✅ Redis connection established")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        settings.cache_client_connector = None
        settings.cache_client_params = None

    try:
        # Stablis connection to clickhouse db
        clickhouse_params = ConnParams(
            engine="clickhouse",
            params={
                "host": settings.CLICKHOUSE_HOST,
                "username": settings.CLICKHOUSE_USER,
                "user": settings.CLICKHOUSE_USER,
                "password": "x",
                "port": settings.CLICKHOUSE_PORT,
                "database": settings.CLICKHOUSE_DB,
            },
        )
        clickhouse_connector = ConnServices.open_persistant_connection(clickhouse_params)
        settings.clickhouse_client_connector = clickhouse_connector
        settings.clickhouse_client_params = clickhouse_params
        print("✅ ClickHouse connection established")
    except Exception as e:
        print(f"⚠️ ClickHouse connection failed: {e}")
        settings.clickhouse_client_connector = None
        settings.clickhouse_client_params = None

    print("🚀 Application startup completed")
    yield
    # connector.close()
    # cache_connector.close()


app = App(
    **settings.fastapi_settings,
    modules=[
        DataSourceModule,
        DiscoveryEngineModule,
        ConnectionModule,
        QuerySetModule,
        DatasetModule,
        TreeModule,
    ],
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
