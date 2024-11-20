from os import getenv
from os import environ
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, validator
from src.infrastructure.mongo_manager.mongo_db_connection import MongoDBConnection
from src.domain.connection.models import DBManager, ConnParams

load_dotenv()


class AppSetting(BaseSettings):
    # FastAPI settings
    DEBUG: bool = getenv('DEBUG', True)
    TITLE: str = 'Kimball API'
    VERSION: str = '0.1.0'
    DESCRIPTION: str = 'Kimball backend endpoints'

    # Mongo settings
    MONGO_HOST: str = getenv('MONGO_HOST', 'localhost:27017')
    MONGO_PORT: int = getenv('MONGO_PORT', 27017)
    MONGO_DB: str = getenv('MONGO_DB', 'kimball')
    MONGO_USER: str = getenv('MONGO_USER', '')
    MONGO_PASS: str = getenv('MONGO_PASS', '')

    ALLOWED_ORIGINS: Any = getenv('ALLOWED_ORIGINS')

    @validator('ALLOWED_ORIGINS', pre=True, always=True)
    def assemble_allowed_origins(v: Optional[str]) -> List[str]:
        if isinstance(v, str):
            return v.split(',') if v else []
        return v

    @property
    def fastapi_settings(self) -> Dict[str, Any]:
        return {
            "debug": self.DEBUG,
            "title": self.TITLE,
            "version": self.VERSION,
            "description": self.DESCRIPTION,
        }

    @property
    def mongo_client(self) -> MongoDBConnection:
        connection_string = "mongodb://"
        if self.MONGO_USER and self.MONGO_PASS:
            connection_string = f"mongodb+srv://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}"
        else:
            connection_string = f"mongodb+srv://{self.MONGO_HOST}:{self.MONGO_PORT}"

        return MongoDBConnection(connection_string=connection_string)

    db_client: DBManager = None
    db_client_params: ConnParams = None

    # @property
    # def db_client(self) -> DBManager:
    #     return None

    # @self_db_client.setter
    # def self_db_client(self, db_manager: DBManager):
    #     self.self_db_client = db_manager


settings = AppSetting()
