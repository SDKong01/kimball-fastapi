from src.interface.dataset.controller import DatasetController
from src.application.dataset.services import DatasetAppServices


class DatasetModule:
    def __init__(self):
        self.providers = [DatasetAppServices]
        self.controllers = [DatasetController]
