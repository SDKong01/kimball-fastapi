from src.interface.queryset.controller import QuerySetController
from src.application.queryset.services import QuerySetAppServices


class QuerySetModule:
    def __init__(self):
        self.providers = [QuerySetAppServices]
        self.controllers = [QuerySetController]
