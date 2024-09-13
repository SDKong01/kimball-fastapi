from typing import Dict
from pymongo import MongoClient


class MongoDBConnection:
    """
    A class for managing MongoDB connections using a modified Singleton pattern that
    creates and reuses instances based on unique connection strings.

    This implementation ensures that only one MongoClient instance is created
    per connection string, facilitating efficient connections management
    to multiple MongoDB databases or configurations.

    :param connection_string: A MongoDB connection URI as a string.
    :type connection_string: str

    :Example:

    >>> connection1 = MongoDBConnection(""mongodb+server://connection-uri-1.mongodb.net/")
    >>> connection2 = MongoDBConnection("mongodb+server://connection-uri-2.mongodb.net/")
    >>> assert connection1 is not connection2
    """

    _instances: Dict[str, MongoClient] = {}

    def __new__(
        cls, connection_string: str = None, connection_id: str = None
    ) -> MongoClient:
        """
        Creates a new MongoClient instance for a given connection string if one does not already exist,
        otherwise returns the existing instance.

        :param connection_string: The MongoDB connection URI.
        :type connection_string: str
        :raises ValueError: If the connection string is empty.
        :return: An instance of MongoClient for the given connection string.
        :rtype: MongoClient
        """
        connection_id = connection_id or connection_string
        if connection_id not in cls._instances:
            if not connection_string:
                raise ValueError(
                    f"Connection string for '{connection_string}' is empty."
                )
            cls._instances[connection_id] = MongoClient(
                connection_string, connect=False
            )
        return cls._instances[connection_id]

    def __del__(self):
        """
        Closes the MongoClient connection when the instance is deleted.
        """
        for key, value in self._instances.items():
            value.close()
            del self._instances[key]
