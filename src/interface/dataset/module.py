from src.interface.dataset.controller import (
    DatasetController,
    MetadataController,
    ForecastController,
)
from src.application.dataset.services import (
    DatasetAppServices,
    MetadataAppServices,
    ForecastAppServices,
)


class DatasetModule:
    def __init__(self):
        self.providers = [DatasetAppServices, MetadataAppServices, ForecastAppServices]
        self.controllers = [DatasetController, MetadataController, ForecastController]
