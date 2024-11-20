from psycopg2 import connect


class PostgresConnection:
    _instances = {}

    def __new__(cls, connection_string: str = None, connection_id: str = None):
        connection_id = connection_id or connection_string
        if connection_id not in cls._instances:
            if not connection_string:
                raise ValueError(
                    f"Connection string for '{connection_string}' is empty."
                )
            cls._instances[connection_id] = connect(connection_string)
        return cls._instances[connection_id]

    def __del__(self):
        for key, value in self._instances.items():
            value.close()
            del self._instances[key]
