from uuid import UUID, uuid4
from dataclass_type_validator import dataclass_validate
from dataclasses import dataclass
from typing import List, Union

from src.domain.data_source.exceptions import InvalidFormatException, InvalidFileType


@dataclass_validate
@dataclass(frozen=True)
class DataSourceDTO:
    id: Union[str, UUID]
    created_at: str
    updated_at: str

    def __post_init__(self):
        self.validate_id()

    def validate_id(self):
        try:
            UUID(self.id)
        except ValueError:
            raise InvalidFormatException(item="id", detail="Invalid UUID format")


class DataSourceFactory:
    @staticmethod
    def build_entity_without_id(created_at: str, updated_at: str) -> DataSourceDTO:
        id = uuid4()
        return DataSourceDTO(id=id, created_at=created_at, updated_at=updated_at)
