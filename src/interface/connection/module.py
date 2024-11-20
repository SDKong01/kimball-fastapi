from src.interface.connection.controller import ConnectionController
from src.application.connection.services import ConnectionAppServices


class ConnectionModule:
    def __init__(self):
        self.providers = [ConnectionAppServices]
        self.controllers = [ConnectionController]
