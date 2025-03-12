from typing import List, Dict, Any
from datetime import datetime, date

from src.domain.connection.models import DBManager
from src.domain.queryset.models import Query, Filter, DimmensionalStructure
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = []
        self.pivot_query = ""
        self.group_by = ""
        self.join_on = ""

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

    @property
    def fields(self) -> str:
        return ", ".join(self._fields)

    @fields.setter
    def fields(self, value):
        self._fields.append(value)

    def process_response(self, response):
        return list(set(item[0] for item in response))

    def _pivot_query(self, query=Query, dim_structure=DimmensionalStructure, **kwargs):
        schema = query.schema
        main_table = query.table
        pivot_table = dim_structure.pivot_tables_map.get(query.pivot)  # dim_vehicle
        pivot_column = query.pivot  # vehicle

        where_statement = "WHERE " if query.filters else ""

        for q in query.filters:
            q = Filter(**q) if isinstance(q, dict) else q
            op = self.operators_translation.get(q.operator)
            if op:
                where_statement += f's."{q.field}"'
                where_statement += f" {op} '{q.value}' OR "

        where_statement = where_statement[:-4]

        group_by: List[str] = query.group_by

        with self.conn.cursor() as cursor:
            cursor.execute(f"SELECT {pivot_column} FROM {schema}.{pivot_table}")
            pivot_values = cursor.fetchall()
        pivot_values = list(
            set(item[0] for item in pivot_values)
        )  # ['car', 'truck', 'motorcycle']
        column_dim = dim_structure.pivot_columns_map.get(pivot_table).get(
            "column_dim"
        )  # vehicle_model
        column_data = dim_structure.pivot_columns_map.get(pivot_table).get(
            "column_data"
        )  # Model
        fild_agg = dim_structure.field_aggregate  # Sales

        select_statement = f's."{query.date_column}", '
        for value in pivot_values:
            _value = f"'{value}'"
            select_statement += f'SUM(CASE WHEN v."{pivot_column}" = {_value} THEN s."{fild_agg}" ELSE 0 END) AS "{value}",'
        select_statement = select_statement.removesuffix(",")
        query_string = (
            f'SELECT {select_statement} '
            f'FROM {schema}."{main_table}" s '
            f'JOIN {schema}."{pivot_table}" v '
            f'ON s."{column_data}" = v."{column_dim}" '
            f'{where_statement}'
            f'GROUP BY s."{query.date_column}"'
        )
        self.pivot_query = query_string

    pivot_set_name = "pv"
    data_set_name = "ds"
    dim_set_name = "dm"

    def _group_by_query(
        self,
        query: Query,
        dim_structure: DimmensionalStructure,
        **kwargs,
    ):
        if not query.group_by:
            return
        data_table_name = self.pivot_set_name if query.pivot else self.data_set_name

        schema = query.schema
        main_table = query.table

        is_raw_column = query.group_by in dim_structure.fields_raw
        if is_raw_column:
            self.fields = f'{data_table_name}."{query.group_by}",'
            self.group_by = f'GROUP BY ds."{query.group_by}"'
            return

        clean_group_by = query.group_by.replace("*", "")
        dim_table = dim_structure.pivot_tables_map.get(clean_group_by)

        column_dim = dim_structure.pivot_columns_map.get(dim_table).get(
            "column_dim"
        )  # vehicle_model
        column_data = dim_structure.pivot_columns_map.get(dim_table).get("column_data")

        is_date = dim_table == dim_structure.table_calendar_dimension

        self.join_on = (
            f' JOIN {schema}."{dim_table}" {self.dim_set_name} '
            f' ON {data_table_name}."{column_data}"{"::Date" if is_date else ""} = {self.dim_set_name}."{column_dim}" '
        )

        group_by = f' GROUP BY {self.dim_set_name}."{clean_group_by}"'

        _fields = f'{self.dim_set_name}."{clean_group_by}"'

        if dim_table == dim_structure.table_calendar_dimension:
            _fields = _fields + ' AS "Calendar Date"'
        self.fields = _fields
        self.group_by = group_by

    def _group_by_naive(self, query: Query, **kwargs):
        group_by = f'GROUP BY "{query.group_by}"' if query.group_by else ""
        return group_by

    def _set_fields(self, query: Query, dim_structure: DimmensionalStructure):
        is_group_by = bool(self.group_by)
        if not query.fields and not is_group_by:
            self.fields = "*"
            return

        fields = query.fields or []

        def prefix(field: str):
            if query.pivot and not field in dim_structure.fields_raw:
                return self.pivot_set_name
            else:
                return self.data_set_name

        for f in fields:
            pre = prefix(f)
            if isinstance(f, dict):
                f = Filter(**f)
            op = self.aggregators_translation.get(f.operator, "")
            if op:
                self.fields = f'{op}({pre}."{f.field}") AS "{op.lower()}_{f.field}"'
            elif f.operator in ["fields", "eq"]:
                self.fields = (
                    f'{self.data_set_name}."{f.field}"'
                    if not query.pivot
                    else f'{self.dim_set_name}."{f.field}"'
                )
                if is_group_by:
                    self.group_by += f', "{f.field}"'
            elif f.operator == "field_as":
                self.fields = f'"{f.field}" AS "{f.value}"'

    def _kwargs_to_query(self, query=Query, **kwargs):
        schema = query.schema
        table = query.table
        if not schema or not table:
            raise Exception("Schema and table are required")
        has_pivot = query.pivot
        dim_structure = kwargs.get("dim_structure")
        if has_pivot:
            if not dim_structure:
                raise Exception("Dimmensional structure is required")
            self._pivot_query(query=query, dim_structure=dim_structure)

        where_statement = "WHERE " if query.filters else ""
        order_by_statement = f'ORDER BY "{query.order_by}"' if query.order_by else ""
        self._group_by_query(query=query, dim_structure=dim_structure)
        self._set_fields(query=query, dim_structure=dim_structure)

        limit_statement = f'LIMIT {query.limit}' if query.limit else ""

        for q in query.filters:
            q = Filter(**q) if isinstance(q, dict) else q
            op = self.operators_translation.get(q.operator)
            if op:
                where_statement += f'{self.data_set_name}."{q.field}"'
                where_statement += f" {op} '{q.value}' OR "
                # where_statement += (
                #     f"{self.data_set_name}.{q.field} {op} '{q.value}' OR "
                # )

        where_statement = where_statement[:-4]

        # fields_statement = self.fields.removesuffix(",")
        source_data_nickname = self.pivot_set_name if has_pivot else self.data_set_name
        if not has_pivot:
            query_string = (
                f"SELECT {self.fields} "
                f"FROM {schema}.{table} {source_data_nickname} "
                f"{self.join_on} "
                f"{where_statement} "
                f"{self.group_by} "
                f"{order_by_statement} "
                f"{limit_statement}"
            )
            print(query_string)
        if has_pivot and not query.group_by and not query.fields:
            query_string = self.pivot_query
        if has_pivot and (query.group_by or query.fields):
            query_string = (
                f"WITH pivot_table as ({self.pivot_query}) "
                f"SELECT {self.fields} "
                f"FROM pivot_table {self.pivot_set_name}"
                f"{self.join_on} "
                f"{self.group_by} "
                f"{order_by_statement} "
                f"{limit_statement}"
            )
        print(query_string)

        query_string = query_string + self.finish_query

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

    def list_fields(self, query=Query, **kwargs):
        available_fiels = []
        dim_structure = kwargs.get("dim_structure")
        if not dim_structure:
            raise Exception("Dimmensional structure is required")
        if query.pivot:
            schema = query.schema
            pivot_table = dim_structure.pivot_tables_map.get(query.pivot)  # dim_vehicle
            pivot_column = query.pivot  # vehicle
            with self.conn.cursor() as cursor:
                cursor.execute(f"SELECT {pivot_column} FROM {schema}.{pivot_table}")
                pivot_values = cursor.fetchall()
            _pivot_fields = list(set(item[0] for item in pivot_values))
            for f in _pivot_fields:
                available_fiels += [
                    f"SUM.{f}",
                    f"AVG.{f}",
                    f"MAX.{f}",
                    f"MIN.{f}",
                    f"COUNT.{f}",
                ]
        else:
            aggregated_fields = dim_structure.field_aggregate
            available_fiels += [
                f"SUM.{aggregated_fields}",
                f"AVG.{aggregated_fields}",
                f"MAX.{aggregated_fields}",
                f"MIN.{aggregated_fields}",
                f"COUNT.{aggregated_fields}",
            ]

        available_fiels += dim_structure.fields_raw
        return available_fiels

    def list_group_by(self, query: Query = None, **kwargs):
        dim_structure = kwargs.get("dim_structure")
        if not dim_structure:
            raise Exception("Dimmensional structure is required")
        return dim_structure.pivot_options
