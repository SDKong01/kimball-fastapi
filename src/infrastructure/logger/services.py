import logging


logger = logging.getLogger(__name__)


class AttributeLogger:
    """
    The AttributeLogger is a logging helper class that stores a set of
    attributes that are automatically inserted as extra params on every log
    call.
    """

    # logger: logging.Logger
    attributes: dict = {}

    _instance = None

    def __new__(cls, **attr):
        if not cls._instance:
            cls._instance = super(AttributeLogger, cls).__new__(cls)
            # Initialize the instance once
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, **attr):
        self.logger = logging.getLogger(__name__)
        self.attributes = attr

    def info(self, msg, *args, **kwargs):
        kwargs["extra"] = self.attributes
        kwargs["stacklevel"] = 2
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        kwargs["extra"] = self.attributes
        kwargs["stacklevel"] = 2
        self.logger.error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        kwargs["extra"] = self.attributes
        kwargs["stacklevel"] = 2
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        kwargs["extra"] = self.attributes
        kwargs["stacklevel"] = 2
        self.logger.warning(msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        kwargs["extra"] = self.attributes
        kwargs["stacklevel"] = 2
        self.logger.fatal(msg, *args, **kwargs)

    def with_attributes(self, **kwargs):
        new_attrs = self.attributes.copy()
        new_attrs.update(kwargs)
        return AttributeLogger(self.logger, **new_attrs)


def logger_dpf():
    return AttributeLogger()
