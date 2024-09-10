from os import getenv
from os import environ
from nest.core.app import App
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.interface.data_source.module import DataSourceModule
from src.config import settings


@asynccontextmanager
async def lifespan(app: App):
    print(getenv('ALLOWED_ORIGINS', 'http://localhost').split(','))
    pass


app = App(
    **settings.fastapi_settings,
    modules=[DataSourceModule],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
