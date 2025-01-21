from typing import List, Dict, Any
from datetime import datetime, date

from src.domain.connection.models import DBManager
from src.domain.queryset.models import Query, Filter
from src.constants import (
    EQUAL,
    NOT_EQUAL,
    GREATER_THAN,
    GREATER_THAN_EQUAL,
    LESS_THAN,
    LESS_THAN_EQUAL,
    IN,
    NOT_IN,
    LIKE,
    NOT_LIKE,
)


class SQLManager(DBManager):

    operators_translation = {
        EQUAL: "=",
        NOT_EQUAL: "!=",
        GREATER_THAN: ">",
        GREATER_THAN_EQUAL: ">=",
        LESS_THAN: "<",
        LESS_THAN_EQUAL: "<=",
        IN: "IN",
        NOT_IN: "NOT IN",
        LIKE: "LIKE",
        NOT_LIKE: "NOT LIKE",
    }

    finish_query = ";"

    query_list_tables = (
        "SELECT table_name FROM information_schema.tables WHERE table_schema = %s;"
    )
    query_list_schemas = (
        "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;"
    )
    query_list_databases = (
        "SELECT datname FROM pg_database WHERE datistemplate = false;"
    )

    def process_response(self, response):
        return list(set(item[0] for item in response))

    def _kwargs_to_query(self, query=Query, **kwargs):
        schema = query.schema
        table = query.table
        print(query)
        if not schema or not table:
            raise Exception("Schema and table are required")
        where_statement = "WHERE " if query.filters else ""

        def is_number(value: str) -> bool:
            try:
                int(value)
                return True
            except ValueError:
                pass

            try:
                float(value)
                return True
            except ValueError:
                False

            return False

        for q in query.filters:
            if isinstance(q, dict):
                q = Filter(**q)
            op = self.operators_translation.get(q.operator)
            if op:
                if is_number(q.value):
                    where_statement += f"{q.field} {op} {q.value} AND "
                else:
                    where_statement += f"{q.field} {op} '{q.value}' AND "

        where_statement = where_statement[:-5]

        fields = "*"
        if query.fields:
            fields = ", ".join(query.fields)

        query_string = f"SELECT {fields} FROM {schema}.{table} {where_statement}{self.finish_query}"
        return query_string

    def _parse_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        _row = []
        for value in row:
            if isinstance(value, date):
                _row.append(value.isoformat())
            else:
                _row.append(value)
        return _row

    def create(self, *args):
        pass

    def retrieve(self, query, **kwargs):
        parsed_query = self._kwargs_to_query(query=query, **kwargs)
        with self.conn.cursor() as cursor:
            cursor.execute(parsed_query)
            response = cursor.fetchall()
        return self.process_response(response)

    def raw_query(self, query):
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            response = list(cursor.fetchall())

        return response

    def list_tables(self, *args, **kwargs) -> List[str]:
        schema = kwargs.get("schema")
        with self.conn.cursor() as cursor:
            cursor.execute(self.query_list_tables, (schema,))
            response = cursor.fetchall()
        return self.process_response(response)

    def list_schemas(self, *args, **kwargs) -> List[str]:
        with self.conn.cursor() as cursor:
            cursor.execute(self.query_list_schemas)
            response = cursor.fetchall()
        return self.process_response(response)

    def list_databases(self, *args, **kwargs) -> List[str]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                self.query_list_databases,
            )
            response = cursor.fetchall()
            print("response", response)
            print("response", response.__class__)
        return self.process_response(response)

    def to_json(
        self, query=Query, orient: str = "records", **kwargs
    ) -> List[Dict[str, Any]]:
        parsed_query = self._kwargs_to_query(query=query, **kwargs)
        if orient == "records":
            with self.conn.cursor() as cursor:
                cursor.execute(parsed_query)
                column_names = [desc[0] for desc in cursor.description]
                records = [
                    dict(zip(column_names, self._parse_row(row)))
                    for row in cursor.fetchall()
                ]

            return records
