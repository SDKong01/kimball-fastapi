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
from src.domain.connection.mongo.client import MongoManager, MongoClientConn
from src.config import settings
from src.domain.connection.models import (
    ConnClient,
    ConnParams,
    SingleConnFactory,
    DBManager,
)


@asynccontextmanager
async def lifespan(app: App):
    # Connect to app MongoDB
    id = MongoClientConn.stablis_new_conn(
        host=settings.MONGO_HOST,
        username=settings.MONGO_USER,
        password=settings.MONGO_PASS,
    )
    params = ConnParams(
        id=id,
        engine="mongodb",
        params={
            "host": settings.MONGO_HOST,
            "username": settings.MONGO_USER,
            "password": settings.MONGO_PASS,
        },
    )
    db = MongoManager(conn_params=params)
    db.conn()
    settings.db_client = db
    settings.db_client_params = params
    # print("Connected to self db")
    # setattr(settings, "db_client", db.conn())
    # settings.slf_db_client = db.conn()
    yield
    del db


app = App(
    **settings.fastapi_settings,
    modules=[DataSourceModule, DiscoveryEngineModule, ConnectionModule],
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
