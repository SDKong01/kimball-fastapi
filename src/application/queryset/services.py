from src.domain.queryset.models import Query
from src.domain.connection.models import ConnParams
from src.domain.connection.services import ConnServices
from src.domain.queryset.services import QueryServices, QuerySet
from src.domain.dataset.services import MetadataServices


class QuerySetAppServices:
    def _remove_bytes_and_lob(self, obj):
        if isinstance(obj, dict):
            return {k: self._remove_bytes_and_lob(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._remove_bytes_and_lob(i) for i in obj]
        elif isinstance(obj, bytes):
            return str(obj.decode('utf-8'))
        elif hasattr(obj, 'read') and not isinstance(
            obj, str
        ):  # Check if it's a LOB object
            response = obj.read()
            response = (
                response.decode('utf-8') if isinstance(response, bytes) else response
            )
            return response
        else:
            return obj

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
        response = queryset.to_json()
        response = self._remove_bytes_and_lob(response)
        return response

    def list_date_columns(self, conn_params: ConnParams, query: Query, is_cached: bool):
        data = self.run_query(conn_params=conn_params, query=query, is_cached=is_cached)
        columns_data = MetadataServices().compute_columns(data)
        date_column = columns_data.get("date_column")
        if date_column:
            return [
                date_column,
            ]
        return []

    def delete():
        pass
