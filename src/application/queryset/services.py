from src.domain.queryset.models import Query
from src.domain.connection.models import ConnParams
from src.domain.connection.services import ConnServices
from src.domain.queryset.services import QueryServices, QuerySet


class QuerySetAppServices:
    def retrieve(self, query: Query):
        response = QueryServices().retrieve(query=query)
        return response

    def create(self, query: Query, is_cached: bool = False) -> Query:
        response = QueryServices().create(query=query)
        return response

    def update(self, query: Query) -> Query:
        response = QueryServices().update(query=query)
        return response

    def delete(self):
        return "QuerysetAppServices.delete"

    def run_query(self, conn_params: ConnParams, query: Query, is_cached: bool):
        result = QueryServices().retrieve(query=query)
        db_manager = ConnServices.get_db_manager(conn_params=conn_params)

        queryset = QuerySet(
            query=result,
            db_manager=db_manager,
            is_cached=is_cached,
        )
        return queryset.to_json()

    def delete():
        pass
