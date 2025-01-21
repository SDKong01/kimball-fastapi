from typing import List, Dict, Any
from datetime import datetime, date

from src.domain.connection.models import DBManager
from src.domain.queryset.models import Query, Filter
from src.domain.connection.managers.sql import SQLManager


class OracleManager(SQLManager):
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
