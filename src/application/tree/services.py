from src.domain.connection.models import DBManager, ConnParams
from src.domain.queryset.models import Query, Filter, DimmensionalStructure
from src.domain.queryset.services import QuerySet, QueryServices
from src.domain.connection.services import ConnServices
from src.config import settings


class TreeAppServices:
    def __init__(self):
        self.sys_conn: DBManager = ConnServices.get_db_manager(
            conn_params=settings.db_client_params
        )
        query = Query(
            filters=[],
            collection="tree_gs",  # TODO: remove hardcoded value
            db=settings.MONGO_DB,
        )
        self.sys_query: QuerySet = QuerySet(query=query, db_manager=self.sys_conn)

    def list_childs(self, node_id: str):
        childs = self.sys_query.filter(parent_id=int(node_id))
        return childs.to_json()

    def recursive_list_childs(self, node_id: str, sack: list = [], level: int = 0):
        if level > 3:
            return

        childs = self.list_childs(node_id)
        for child in childs:
            child_id = child.get("id_centro_costos")  # TODO: remove hardcoded value
            # child_of_childs = qs.filter(parent_id=child_id).to_json()
            # if not child_of_childs:
            if len(str(child_id)) == 6:
                sack.append(child)
            else:
                self.recursive_list_childs(child_id, sack, level=level + 1)

    def list_last_childs(self, node_id: str):
        last_childs = []
        self.recursive_list_childs(node_id, sack=last_childs)

        return last_childs
