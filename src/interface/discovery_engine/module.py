from src.interface.discovery_engine.controller import DiscoveryEngineController
from src.application.discovery_engine.services import DiscoveryEngineAppServices


class DiscoveryEngineModule:
    def __init__(self):
        self.providers = [DiscoveryEngineAppServices]
        self.controllers = [DiscoveryEngineController]
