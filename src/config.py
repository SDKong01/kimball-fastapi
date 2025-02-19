from os import getenv
from ast import literal_eval
from os import environ
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, validator
from src.infrastructure.mongo_manager.mongo_db_connection import MongoDBConnection


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
    MONGO_IS_ATLAS_CLUSTER: bool = False

    # Redis settings
    REDIS_HOST: str = getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = getenv('REDIS_PORT', 6379)
    REDIS_PASS: str = getenv('REDIS_PASS', '')
    REDIS_DB: int = getenv('REDIS_DB', 0)

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

    # @property
    # def mongo_client(self) -> MongoDBConnection:
    #     connection_string = "mongodb://"
    #     if self.MONGO_USER and self.MONGO_PASS:
    #         connection_string = f"mongodb+srv://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}"
    #     else:
    #         connection_string = f"mongodb+srv://{self.MONGO_HOST}:{self.MONGO_PORT}"

    #     return MongoDBConnection(connection_string=connection_string)

    shared_instances: Dict[str, Any] = {}

    db_client_connector: Any = None
    db_client_params: Any = None

    cache_client_connector: Any = None
    cache_client_params: Any = None

    testing_client: str = getenv('TESTING_CLIENT', 'test_client')

    db_name: str = getenv('DB_NAME', testing_client)


settings = AppSetting()
