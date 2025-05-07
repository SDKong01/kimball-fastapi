import re
from itertools import count
from typing import List, Dict, Any
from datetime import datetime, date

from src.domain.connection.models import DBManager
from src.domain.queryset.models import Query, Filter
from src.domain.connection.managers.sql import SQLManager


class MergeTreeManager(SQLManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = ["*"]
        self._filters = []
        self._order_by = "ORDER BY 1"

        self._pivot_fields_names = []

    table_alias = "gm"

    @property
    def fields(self):
        _fields = self._fields[1:] if len(self._fields) > 1 else self._fields
        return ", ".join(_fields)

    @fields.setter
    def fields(self, value):
        self._fields.append(value)

    @fields.deleter
    def fields(self):
        self._fields = ["*"]

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
        # if not query.pivot:
        #     self.fields = "*"
        #     return

        def parse_field_name(operation, fact_column, field_name) -> str:
            col_name = fact_column
            if field_name != fact_column:
                col_name = f"{fact_column} ({field_name})"
            if query.filters:
                col_name = (
                    f"{col_name} ({' · '.join([f.value for f in query.filters])})"
                )
            return col_name

        default_fact_column = "sales_revenue"  # TODO: remove hardcoded value

        for p in query.pivot or []:
            pivot_column = p["pivot"]
            column_name = p["column"]
            fact_column = p.get("fact_column", default_fact_column)
            agg_type = p.get("agg", "SUM").upper()
            field_name = self._clean_str(column_name)
            field_name = parse_field_name(agg_type, fact_column, field_name)
            self._pivot_fields_names.append(field_name)
            self.fields = (
                f"{agg_type}(CASE WHEN {self.table_alias}.{pivot_column} = '{column_name}' THEN toFloat64({self.table_alias}.{fact_column}) ELSE 0 END) AS "
                + f'"{field_name}"'
            )

        if query.pivot:
            return

        for f in query.fields:
            if isinstance(f, dict):
                f = Filter(**f)
            op = self.aggregators_translation.get(f.operator, "")
            field_name = parse_field_name(op, f.field, f.field)
            if op:
                self.fields = f'{op}(toFloat64("{f.field}")) AS "{field_name}"'
            elif f.operator in ["fields", "eq"]:
                self.fields = f'"{f.field}"'
            elif f.operator == "field_as":
                self.fields = f'"{f.field}" AS "{f.value}"'

    def _set_stats_fields(self, pivot):
        # if not query.pivot:
        #     self.fields = "*"
        #     return

        def parse_field_name(operation, fact_column, field_name):
            return f"{operation} of {fact_column} at {field_name}"

        default_fact_column = "sales_revenue"  # TODO: remove hardcoded value

        aggs = ["min", "max", "avg", "stddevPop", "uniqExact"]

        pivot_column = pivot["pivot"]
        column_name = pivot["column"]
        fact_column = pivot.get("fact_column", default_fact_column)
        for agg_type in aggs:
            field_name = self._clean_str(column_name)
            field_name = parse_field_name(agg_type, fact_column, field_name)
            self.fields = (
                f"{agg_type}(CASE WHEN {self.table_alias}.{pivot_column} = '{column_name}' THEN toFloat64({self.table_alias}.{fact_column}) ELSE null END) AS "
                + f'"{agg_type}"'
            )
        # self.fieids = self.fields = (
        #     f"countIf(CASE WHEN {self.table_alias}.{pivot_column} = '{column_name}' THEN toFloat64({self.table_alias}.{fact_column}) END IS NULL) AS "
        #     + f'"nulls"'
        # )

    def _set_group_by(self, query: Query):
        if not query.group_by:
            return ""

        self.fields = f"{self.table_alias}.{query.group_by} AS " + '"Calendar Date"'
        # self._order_by = f"ORDER BY {query.db}.{query.group_by}"
        # group_by_statement = f'GROUP BY {query.db}.{query.group_by}'
        self._order_by = f'ORDER BY "Calendar Date"'
        group_by_statement = f'GROUP BY "Calendar Date"'
        return group_by_statement

    def _set_filters(self, query: Query):
        if not query.filters:
            return ""

        where_statement = "WHERE "

        ands: List[str] = []
        filters_map: Dict[str, List[str]] = {}

        for q in query.filters:
            q = Filter(**q) if isinstance(q, dict) else q
            op = self.operators_translation.get(q.operator)
            if not op:
                continue

            filters_map.setdefault(q.field, []).append(q.value)
            # where_statement += f"{q.field} {op} '{q.value}' OR "

        ins_statemens = []
        for field, values in filters_map.items():
            _f = field + " IN " + "(" + ", ".join([f"'{v}'" for v in values]) + ")"
            ins_statemens.append(_f)

        ands = list("AND" for x in range(len(ins_statemens))) or [
            " ",
        ]
        ands[-1:] = " "

        for statement, operator in zip(ins_statemens, ands):
            where_statement += f"{statement} {operator} "

        return where_statement

    def _kwargs_to_query(self, query=Query, **kwargs):
        only_columns = kwargs.get("available_fields", False)

        if query.distinct_field:
            return f"SELECT DISTINCT {query.distinct_field} FROM {query.db}.{query.table} LIMIT 200"

        table = query.table
        db = query.db
        # if not schema or not table:
        #     raise Exception("Schema and table are required")

        group_by_statement = self._set_group_by(query)
        where_statement = self._set_filters(query)
        limit_statement = f'LIMIT {query.limit}' if query.limit else ""
        if only_columns:
            limit_statement = 'LIMIT 0'

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

    def stats(self, query=Query, **kwargs):
        table = query.table
        db = query.db
        # if not schema or not table:
        #     raise Exception("Schema and table are required")
        where_statement = "WHERE " if query.filters else ""
        # group_by_statement = self._set_group_by(query)
        limit_statement = f'LIMIT {query.limit}' if query.limit else ""

        for q in query.filters:
            q = Filter(**q) if isinstance(q, dict) else q
            op = self.operators_translation.get(q.operator)
            if op:
                where_statement += f"{q.field} {op} '{q.value}' OR "

        where_statement = where_statement[:-4]

        query.fields = query.fields or []
        result = []
        column_names = [
            "min",
            "max",
            "mean",
            "stddev",
            "unique",
            #  "missing"
        ]

        query_copy = Query(**query.__dict__)
        query_copy.pivot = []

        for p in query.pivot or []:
            delattr(self, "fields")
            self._set_stats_fields(p)
            query_string = f"SELECT {self.fields} FROM {db}.{table} {self.table_alias} {where_statement} {self.finish_query}"
            # print(query_string)
            response = self.conn.query(query_string)
            _stats = dict(zip(column_names, response.result_rows[0]))
            # print(_stats)
            # _stats = dict(_stats[0])
            _stats["target"] = p["column"]
            _stats["missing"] = 0
            result.append(_stats)
            # print(_stats)

        # print(query_string)
        return result

    def create(self, query=Query, *args):
        if not args:
            raise Exception("No data to insert")
        fields = tuple(args[0].keys())
        table = query.table
        db = query.db

        check_statement = f"SELECT {', '.join(fields)} FROM {db}.{table} WHERE "
        for row in args:
            conditions = " AND ".join(
                [f"{field} = '{value}'" for field, value in row.items()]
            )
            check_statement += f"({conditions}) OR "
        check_statement = check_statement[:-4] + ";"

        existing_records = self.conn.query(check_statement).result_rows
        existing_set = {tuple(record) for record in existing_records}

        rows_to_insert = [
            row for row in args if tuple(row.values()) not in existing_set
        ]

        if not rows_to_insert:
            return True

        parsed_fields = f"({', '.join(fields)})"
        insert_statement = f"INSERT INTO {db}.{table} {parsed_fields} VALUES "
        for row in rows_to_insert:
            insert_statement += f"({', '.join([f"'{x}'" for x in row.values()])}), "
        insert_statement = insert_statement[:-2] + ";"
        self.conn.query(insert_statement)

        return True
