from dataclasses import dataclass


@dataclass(frozen=True)
class BaseExceptionMixin(Exception):
    item: str
    detail: str

    def __str__(self):
        return "{}: {}".format(self.item, self.message)
