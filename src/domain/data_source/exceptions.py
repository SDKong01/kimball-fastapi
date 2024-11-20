from src.infrastructure.exceptions.mixins import BaseExceptionMixin


class DBEngineNotSupported(BaseExceptionMixin):
    pass


class InvalidFormatException(BaseExceptionMixin):
    pass


class InvalidFileType(BaseExceptionMixin):
    pass
