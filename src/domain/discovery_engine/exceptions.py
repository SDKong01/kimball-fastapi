from src.infrastructure.exceptions.mixins import BaseExceptionMixin


class MissingRequiredFieldsException(BaseExceptionMixin):
    pass


class InvalidFormatException(BaseExceptionMixin):
    pass
