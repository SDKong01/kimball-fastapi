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
    MAX_LIMIT_QUERY,
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

    aggregators_translation = {
        "count": "COUNT",
        "sum": "SUM",
        "avg": "AVG",
        "max": "MAX",
        "min": "MIN",
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
        replace_date = kwargs.get("replace_date", False)
        schema = query.schema
        table = query.table
        if not schema or not table:
            raise Exception("Schema and table are required")
        where_statement = "WHERE " if query.filters else ""
        fields_statement = "*,"
        order_by_statement = f'ORDER BY "{query.order_by}"' if query.order_by else ""
        group_by_statement = f'GROUP BY "{query.group_by}"' if query.group_by else ""
        limit_statement = f'LIMIT {query.limit}' if query.limit else ""

        for q in query.filters:
            q = Filter(**q) if isinstance(q, dict) else q
            op = self.operators_translation.get(q.operator)
            if op:
                where_statement += f"{q.field} {op} '{q.value}' OR "

        where_statement = where_statement[:-4]

        query.fields = query.fields or []
        if query.fields:
            fields_statement = ""

        for f in query.fields:
            if isinstance(f, dict):
                f = Filter(**f)
            op = self.aggregators_translation.get(f.operator, "")
            if op:
                fields_statement += f'{op}("{f.field}") AS "{f.field}",'
            elif f.operator in ["fields", "eq"]:
                fields_statement += f'"{f.field}",'
            elif f.operator == "field_as":
                fields_statement += f'"{f.field}" AS "{f.value}",'

        if query.date_column and replace_date:
            if fields_statement == "*,":
                # There is no fields in the query so we need to get the column names
                parsed_query = f"SELECT * FROM {schema}.{table}  {where_statement} {group_by_statement} LIMIT 1{self.finish_query}"
                with self.conn.cursor() as cursor:
                    cursor.execute(parsed_query)
                    column_names = [desc[0] for desc in cursor.description]

                fields_statement = ", ".join(column_names)

            # Replace the date column name with the alias "Calendar Date"
            fields_statement = fields_statement.replace(
                query.date_column, f'{query.date_column} AS "Calendar Date"'
            )

        fields_statement = fields_statement.removesuffix(",")

        query_string = f"SELECT {fields_statement} FROM {schema}.{table} {where_statement} {group_by_statement} {order_by_statement} {limit_statement}{self.finish_query}"
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
        return self.process_response(response)

    def to_json(
        self, query=Query, orient: str = "records", **kwargs
    ) -> List[Dict[str, Any]]:
        print("******************* parsed query *******************")
        print(query)
        parsed_query = self._kwargs_to_query(query=query, **kwargs)
        print("******************* parsed query *******************")
        print(parsed_query)
        if orient == "records":
            with self.conn.cursor() as cursor:
                cursor.execute(parsed_query)
                column_names = [desc[0] for desc in cursor.description]
                records = [
                    dict(zip(column_names, self._parse_row(row)))
                    for row in cursor.fetchall()
                ]

            return records
