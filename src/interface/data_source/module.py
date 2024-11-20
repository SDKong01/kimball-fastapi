from src.interface.data_source.controller import DataSourceController
from src.application.data_source.services import DataSourceAppServices


class DataSourceModule:
    def __init__(self):
        self.providers = [DataSourceAppServices]
        self.controllers = [DataSourceController]
