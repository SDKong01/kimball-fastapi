from src.interface.tree.controller import TreeController
from src.application.tree.services import TreeAppServices


class TreeModule:
    def __init__(self):
        self.providers = [TreeAppServices]
        self.controllers = [TreeController]
