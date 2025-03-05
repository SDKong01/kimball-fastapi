from src.infrastructure.exceptions.mixins import BaseExceptionMixin


class ConnectionMissinParams(BaseExceptionMixin):
    pass


class MethodNotAvailable(BaseExceptionMixin):
    pass


class ArgumentError(BaseExceptionMixin):
    pass


class ConnectionMissing(BaseExceptionMixin):
    pass


class ConnectionError(BaseExceptionMixin):
    pass
