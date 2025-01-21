from typing import List
from src.domain.connection.models import ConnClient


class Services:
    def __init__(self, conn: ConnClient):
        self.conn = conn

    def list_schemas(self) -> List[str]:
        query = self.conn.cursor.execute(
            "SELECT USERNAME FROM ALL_USERS ORDER BY USERNAME;"
        )
        return list(query.fetchall())
