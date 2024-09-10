from dataclasses import dataclass


@dataclass(frozen=True)
class BaseExceptionMixin(Exception):
    item: str
    message: str

    def __str__(self):
        return "{}: {}".format(self.item, self.message)
