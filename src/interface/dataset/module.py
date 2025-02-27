from src.interface.dataset.controller import DatasetController, MetadataController
from src.application.dataset.services import DatasetAppServices, MetadataAppServices


class DatasetModule:
    def __init__(self):
        self.providers = [DatasetAppServices, MetadataAppServices]
        self.controllers = [DatasetController, MetadataController]
