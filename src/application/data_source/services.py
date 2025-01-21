import io
import uuid
import csv
import json
import zipfile
import pandas as pd
from typing import List, Optional
from tempfile import SpooledTemporaryFile, TemporaryFile
from starlette.datastructures import UploadFile
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate
from src.domain.data_source.exceptions import (
    InvalidFormatException,
    DBEngineNotSupported,
)
from src.domain.data_source.services import DataSourceServices
from src.constants import MONGO, POSTGRES, DB_ENGINES
from src.domain.connection.models import (
    ConnParams,
)


class DataSourceDBServices:
    pass


@dataclass_validate
@dataclass(frozen=True)
class CloneParamsDTO:
    engine: str
    conn_id: str
    collection: Optional[str] = None
    db: Optional[str] = None

    def __post_init__(self):
        self.validate_engine()

    def validate_engine(self):
        if self.engine not in DB_ENGINES:
            raise DBEngineNotSupported(
                item="engine", detail=f"Invalid engine, {self.engine} not supported"
            )

    def validate_collection(self):
        if not self.collection:
            raise InvalidFormatException(
                item="collection", detail="Collection name is required"
            )

    def validate_db(self):
        if not self.db:
            raise InvalidFormatException(item="db", detail="DB name is required")

    def validate_conn_id(self):
        if not self.conn_id:
            raise InvalidFormatException(
                item="conn_id", detail="Connection ID is required"
            )
        try:
            uuid.UUID(self.conn_id)
        except ValueError:
            raise InvalidFormatException(item="conn_id", detail="Invalid UUID format")


# services = {
#     MONGO: DataSourceServices.mongo_services,
# }


class DataSourceAppServices:
    ### -------------------- DB Connection --------------------
    # def _get_connector_by_engine(self, engine: str) -> DataSourceDBServices:
    #     return services.get(engine)()

    # def clone_legacy(self, params: CloneParamsDTO, db: str) -> str:
    #     conn_params = ConnParams(
    #         id=params.conn_id,
    #         engine=params.engine,
    #     )
    #     connector = self._get_connector_by_engine(params.engine)(conn_params)
    #     new_items = connector.clone_to_self_db(
    #         collection_origin=params.collection,
    #         db_origin=params.db,
    #         collection_dest=params.collection,
    #         db_dest=db,
    #     )
    #     return new_items

    # def clone(
    #     conn_params: ConnParams, query_params: Query, query_id: str = None
    # ) -> int:
    #     return DataSourceServices.clone(conn_params, db, collection)

    # def save_metadata(
    #     conn_params: ConnParams, query_params: Query, query_id: str = None
    # ) -> int:
    #     return DataSourceServices.save_metadata(conn_params, db, collection)

    ### -------------------- File Upload --------------------

    def upload_file(self, file: UploadFile, db: str) -> int:
        return DataSourceServices.file_services().upload_file(file=file, db=db)
