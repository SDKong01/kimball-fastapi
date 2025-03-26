import re
from typing import List, Dict, Any
from datetime import datetime, date

from src.domain.connection.models import DBManager
from src.domain.queryset.models import Query, Filter
from src.domain.connection.managers.sql import SQLManager


class MergeTreeManager(SQLManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = []
        self._order_by = "ORDER BY 1"

    table_alias = "gm"

    @property
    def fields(self):
        return ", ".join(self._fields)

    @fields.setter
    def fields(self, value):
        self._fields.append(value)

    finish_query = ""

    query_list_tables = """SELECT TABLE_NAME 
    FROM DBA_TAB_COLUMNS 
    WHERE COLUMN_NAME LIKE '%CUSTOMER%' 
       OR COLUMN_NAME LIKE '%DATE%'"""
    query_list_schemas = (
        "SELECT USERNAME AS schema_name FROM ALL_USERS ORDER BY USERNAME"
    )
    query_list_databases = "SELECT USERNAME AS datname FROM DBA_USERS WHERE DEFAULT_TABLESPACE NOT IN ('SYSTEM', 'SYSAUX')"

    def process_response(self, response):
        return list(set(str(item[0]) for item in response))

    def _parse_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        _row = []
        for value in row:
            if isinstance(value, date):
                _row.append(value.isoformat())
            else:
                _row.append(value)
        return _row

    def _parse_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        _row = []
        for value in row:
            if isinstance(value, date):
                _row.append(value.isoformat())
            else:
                _row.append(value)
        return _row

    def list_tables(self, *args, **kwargs) -> List[str]:
        with self.conn.cursor() as cursor:
            cursor.execute(self.query_list_tables)
            response = cursor.fetchall()
        return self.process_response(response)

    def list_suggested_tables(self, *args, **kwargs) -> List[str]:
        foreign_keys_query = """SELECT A.TABLE_NAME 
FROM DBA_CONS_COLUMNS A
JOIN DBA_CONSTRAINTS B ON A.CONSTRAINT_NAME = B.CONSTRAINT_NAME
WHERE B.CONSTRAINT_TYPE = 'R'"""

        customer_or_date_query = """SELECT TABLE_NAME 
FROM DBA_TAB_COLUMNS 
WHERE COLUMN_NAME LIKE '%CUSTOMER%' 
   OR COLUMN_NAME LIKE '%DATE%'"""

        aud_or_tran_query = """SELECT TABLE_NAME 
FROM ALL_TABLES 
WHERE TABLE_NAME LIKE '%AUD%' OR TABLE_NAME LIKE '%TRAN%'"""

        queries = [foreign_keys_query, customer_or_date_query, aud_or_tran_query]

        with self.conn.cursor() as cursor:
            suggested_tables = []
            for q in queries:
                cursor.execute(q)
                response = cursor.fetchall()
                suggested_tables += list(set(item[0] for item in response[:10]))

        return suggested_tables

    def list_suggested_views(self, *args, **kwargs) -> List[str]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT view_name FROM all_views WHERE view_name LIKE '%AUD%' OR view_name LIKE '%TRAN%'"
            )
            response = cursor.fetchall()
        return list(response)

    def list_childs(self, pivot: str) -> List[str]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"SELECT table_name FROM all_constraints WHERE r_constraint_name = '{pivot}'"
            )
            response = cursor.fetchall()
        return list(response)

    def _set_fields_nodes(self, query: Query, nodes: List[Dict[str, Any]]):
        if not query.pivot:
            self.fields = "*"
            return

        self.fields = "gm.mes"

        for node in nodes:
            cost_center = node.get("id_centro_costos")
            if not cost_center:
                continue
            self.fields = (
                f"SUM(CASE WHEN {query.db}.id_centro_costos = '{cost_center}' THEN {query.db}.importe_pesos ELSE 0 END) AS "
                + f'"{cost_center}"'
                # + f'"{node.get("nombre")}"'
            )

    def _clean_str(self, field_name: str) -> str:
        return re.sub(
            r'[^a-zA-Z0-9_]',
            '',
            field_name.encode('ascii', 'ignore').decode().replace(" ", "_"),
        )

    def _set_fields(self, query: Query):
        if not query.pivot:
            self.fields = "*"
            return

        fact_column = "sales_revenue"  # TODO: remove hardcoded value

        for p in query.pivot:
            field_name = self._clean_str(p[1])
            self.fields = (
                f"SUM(CASE WHEN {self.table_alias}.{p[0]} = '{p[1]}' THEN {self.table_alias}.{fact_column} ELSE 0 END) AS "
                + f'"{field_name}"'
            )

    def _set_group_by(self, query: Query):
        if not query.pivot or not query.group_by:
            return ""

        self.fields = f"{self.table_alias}.{query.group_by} AS " + '"Calendar Date"'
        # self._order_by = f"ORDER BY {query.db}.{query.group_by}"
        # group_by_statement = f'GROUP BY {query.db}.{query.group_by}'
        self._order_by = f'ORDER BY "Calendar Date"'
        group_by_statement = f'GROUP BY "Calendar Date"'
        return group_by_statement

    def _kwargs_to_query(self, query=Query, **kwargs):
        replace_date = kwargs.get("replace_date", False)
        pivot_childs = kwargs.get("pivot_childs", [])
        only_columns = kwargs.get("available_fields", False)

        if query.distinct_field:
            return f"SELECT DISTINCT {query.distinct_field} FROM {query.db}.{query.table} LIMIT 200"

        table = query.table
        db = query.db
        # if not schema or not table:
        #     raise Exception("Schema and table are required")
        where_statement = "WHERE " if query.filters else ""
        group_by_statement = self._set_group_by(query)
        limit_statement = f'LIMIT {query.limit}' if query.limit else ""
        if only_columns:
            limit_statement = 'LIMIT 0'

        for q in query.filters:
            q = Filter(**q) if isinstance(q, dict) else q
            op = self.operators_translation.get(q.operator)
            if op:
                where_statement += f"{q.field} {op} '{q.value}' OR "

        where_statement = where_statement[:-4]

        query.fields = query.fields or []
        self._set_fields(query)
        query_string = f"SELECT {self.fields} FROM {db}.{table} {self.table_alias} {where_statement} {group_by_statement} {self._order_by} {limit_statement}{self.finish_query}"

        print(query_string)
        return query_string

    def to_json(
        self, query=Query, orient: str = "records", **kwargs
    ) -> List[Dict[str, Any]]:
        only_columns = kwargs.get("available_fields", False)
        parsed_query = self._kwargs_to_query(query=query, **kwargs)
        if orient == "records":
            response = self.conn.query(parsed_query)
            column_names = response.column_names
            if only_columns:
                return list(column_names)
            records = [
                dict(zip(column_names, self._parse_row(row)))
                for row in response.result_rows
            ]

            return records
