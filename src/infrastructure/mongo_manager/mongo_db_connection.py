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

    _instances = {}

    def __new__(cls, connection_string) -> MongoClient:
        """
        Creates a new MongoClient instance for a given connection string if one does not already exist,
        otherwise returns the existing instance.

        :param connection_string: The MongoDB connection URI.
        :type connection_string: str
        :raises ValueError: If the connection string is empty.
        :return: An instance of MongoClient for the given connection string.
        :rtype: MongoClient
        """
        if connection_string not in cls._instances:
            if not connection_string:
                raise ValueError(
                    f"Connection string for '{connection_string}' is empty."
                )
            cls._instances[connection_string] = MongoClient(
                connection_string, connect=False
            )
        return cls._instances[connection_string]
