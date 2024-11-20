from uuid import uuid4, UUID
from dataclass_type_validator import dataclass_validate
from dataclasses import dataclass
from bson import ObjectId
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict, Union

# local imports
from src.config import settings
from src.constants import ENGINES_COLLECTION
from src.infrastructure.mongo_manager.bson_abstract_factory import AbstractBSONFactory
from src.domain.discovery_engine.exceptions import InvalidFormatException, MissingRequiredFieldsException


class SQLDiscovery(ABC):
    def __init__(self, db_conn, *args, **kwargs):
        self.db_conn = db_conn

    def fetchall(self, query, *args, **kwargs):
        result = []
        
        with self.db_conn.cursor() as cursor:
            result = cursor.execute(query, *args)
            result = cursor.fetchall()
            return result
        return result

    @abstractmethod
    def close(self, *args, **kwargs):
        pass


class PGDiscovery(SQLDiscovery):
    def __init__(self, db_conn, *args, **kwargs):
        super().__init__(db_conn, *args, **kwargs)

    def get_schemas(self, *args, **kwargs) -> List[str]:
        query = "SELECT schema_name FROM information_schema.schemata;"
        result = self.fetchall(query)
        return result

    def get_tables_by_shcema(self, schema: str = None, *args, **kwargs):
        query = (
            "SELECT table_name FROM information_schema.tables WHERE table_schema = %s;",
            (schema,),
        )
        result = self.fetchall(*query)
        return result

    def get_columns_by_table(self, table: str, schema: str, *args, **kwargs):
        query = (
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s AND table_schema = %s;",
            (table, schema),
        )
        result = self.fetchall(*query)
        return result

    def close(self, *args, **kwargs):
        self.db_conn.close()
        return None


class EngineRepo(AbstractBSONFactory):
    def __init__(self, collection: str) -> None:
        self.db = settings.mongo_client[settings.MONGO_DB][collection]

    def _convert_object_id(self, document: Dict[str, Any]) -> Dict[str, Any]:
        if '_id' in document and isinstance(document['_id'], ObjectId):
            document['_id'] = str(document['_id'])
        return document

    def insert_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.insert_one(data)

    def update_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.update_one(data)

    def insert_many(self, data: List[Dict[str, Any]], **kwargs) -> List[Any]:
        result = self.db.insert_many(data)
        return result.inserted_ids

    def find_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.find_one(data)

    def find(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        return self.db.find(data)


@dataclass_validate
@dataclass(frozen=True)
class DBSourceDTO:
    schema: str
    table: str


@dataclass_validate
@dataclass(frozen=True)
class EngineDTO:
    id: Optional[str]
    engine_name: str
    catalog: str
    output_table_name: str
    db_source: DBSourceDTO
    data_storage_name: str
    output_table_prefix: Optional[str] = None
    sample_size: Optional[int] = None

    def __post_init__(self):
        self.validate_sample_size()
        self.validate_id()

    def validate_sample_size(self):
        if self.sample_size and self.sample_size < 1:
            raise InvalidFormatException(item="engine", detail="Sample size must be greater than 0")

    def validate_id(self):
        if not self.id:
            return
        try:
            UUID(self.id)
        except ValueError:
            raise InvalidFormatException(item="engine", detail="Invalid UUID format")


class Engine:
    def __init__(
        self,
        id: str,
        engine_name: str,
        catalog: str,
        output_table_name: str,
        data_storage_name: str,
        db_source: Dict[str, str],
        sample_size: Optional[int] = None,
        output_table_prefix: Optional[str] = None,
    ):
        self.id = id
        self.engine_name = engine_name
        self.catalog = catalog
        self.output_table_name = output_table_name
        self.output_table_prefix = output_table_prefix
        self.db_source = db_source
        self.data_storage_name = data_storage_name
        self.sample_size = sample_size
        self.is_valid(raise_exception=True)

    def is_valid(self, raise_exception=False) -> bool:
        # TODO: implement validation
        mandatory_fields = ["id", "engine_name", "catalog", "output_table_name", "db_source", "data_storage_name"]
        for field in mandatory_fields:
            if not getattr(self, field):
                if raise_exception:
                    raise MissingRequiredFieldsException(item="entity", detail=f"Missing required field: {field}")
                return False
        return True

    def save(self):
        self.is_valid(raise_exception=True)
        repo = EngineRepo(collection=ENGINES_COLLECTION)
        repo.insert_one(data=self.__dict__)

    def create_dataset(self, connection: SQLDiscovery):
        # TODO: collection name must be unique and use the user_id as prefix
        # TODO: implement celery task to run the query and store the data
        repo_data = EngineRepo(collection=self.engine_name)
        query = f"SELECT * FROM {self.db_source.get("schema")}.{self.db_source.get("table")}"
        query = (
            query + f" LIMIT {self.sample_size};" if self.sample_size else query + ";"
        )
        result = connection.fetchall(query)
        repo_data.insert_many(data=result)

    def change_name(self, new_name: str) -> "Engine":
        # TODO: check if the name is unique
        self.engine_name = new_name
        return self

    def to_dto(self):
        return EngineDTO(
            id=self.id,
            engine_name=self.engine_name,
            catalog=self.catalog,
            output_table_name=self.output_table_name,
            output_table_prefix=self.output_table_prefix,
            db_source=self.db_source,
            data_storage_name=self.data_storage_name,
            sample_size=self.sample_size,
        )

    def __dict__(self):
        return self.to_dto().__dict__

    def __repr__(self):
        return f"Engine({self.engine_name})"

    def __str__(self):
        return f"Engine: {self.engine_name}"


class EngineFactory:
    @staticmethod
    def build_entity_without_id(engine_dto: EngineDTO) -> Engine:
        if isinstance(db_source, dict):
            db_source = DBSourceDTO(**db_source)
        id = str(uuid4())
        return Engine(
            id=id,
            engine_name=engine_dto.engine_name,
            catalog=engine_dto.catalog,
            output_table_name=engine_dto.output_table_name,
            output_table_prefix=engine_dto.output_table_prefix,
            db_source=db_source,
            data_storage_name=engine_dto.data_storage_name,
            sample_size=engine_dto.sample_size,
        )
    
    @staticmethod
    def build_entity_with_id(engine_dto: EngineDTO) -> Engine:
        if isinstance(db_source, dict):
            db_source = DBSourceDTO(**db_source)
        return Engine(
            id=engine_dto.id,
            engine_name=engine_dto.engine_name,
            catalog=engine_dto.catalog,
            output_table_name=engine_dto.output_table_name,
            output_table_prefix=engine_dto.output_table_prefix,
            db_source=db_source,
            data_storage_name=engine_dto.data_storage_name,
            sample_size=engine_dto.sample_size,
        )
