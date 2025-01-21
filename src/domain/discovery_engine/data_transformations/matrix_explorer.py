import re
import math
import string
from dateutil.parser import parse
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Type, Any

from dataclasses import dataclass


class MatrixExplorerTransformations:
    def __init__(self, data: Dict[str, Dict[str, str]]):
        # self.data = data
        self.data_list = data
        self.cell_profiles: Dict[str, Dict[str, str]] = {}

    @dataclass
    class CellProfile:
        header: Optional[float] = None
        table: Optional[float] = None
        column: Optional[float] = None
        value_type: Optional[str] = None
        is_null: Optional[bool] = False
        is_index: Optional[float] = None

    @dataclass
    class CellType:
        is_int: Optional[bool]
        is_float: Optional[bool]
        is_bool: Optional[bool]
        is_date: Optional[bool]
        is_str: Optional[bool]
        is_null: Optional[bool]
        is_empty: Optional[bool]

    @dataclass
    class TableData:
        columns_type = List[Any]
        headers = List[str]
        raw_data = List[Any]

    def _is_date(self, value: str) -> bool:
        date_pattern = r'\b(\d{4}[-/]\d{2}[-/]\d{2}(?:[T\s]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?)?|\d{2}[-/]\d{2}[-/]\d{4})\b'
        if re.match(date_pattern, value):
            return True
        # try:
        #     parse(string, fuzzy=False)
        #     return True
        # except:
        #     pass

        # try:
        #     datetime.fromtimestamp(int(value))
        #     return True
        # except:
        #     pass

        # try:
        #     datetime.fromtimestamp(int(value) / 1000)
        #     return True
        # except:
        #     pass

        # return False

    def clean_is_empty(self, value: str) -> bool:
        null_values = ["", " ", "null", "nan", "none"]
        if value and str(value).lower() in null_values:
            return None
        return value

    def get_value_type(self, value: str) -> CellType:
        cell_type = self.CellType(
            is_int=bool(value and str(value).isdigit()),
            is_float=bool(value and str(value).replace(".", "", 1).isdigit()),
            is_date=bool(value and self._is_date(str(value))),
            is_null=None == value,
            is_empty=bool(value and self.clean_is_empty(str(value))),
            is_str=bool(value and not str(value).isdigit()),
            is_bool=bool(value and str(value).lower() in ["true", "false", "1", "0"]),
        )
        return cell_type

    def _all_false(self, iterable) -> bool:
        return all(not element for element in iterable)

    def _find_empy_rows(self, initial: bool = False):
        last_row = max(self.data_list, key=lambda x: x["x"])["x"]  # row = numers
        last_col = max(self.data_list, key=lambda x: x["y"])["y"]  # col = letters

        initial_row = min(self.data_list, key=lambda x: x["x"])["x"]
        initial_col = min(self.data_list, key=lambda x: x["y"])["y"]

        tables = []
        _init_row = None
        _last_row = None
        for row in range(initial_row, last_row + 1):
            values = [
                item["value"]
                for item in filter(lambda item: item["x"] == row, self.data_list)
            ]

            is_empty_row = self._all_false(values)
            # Define initial table row if not defined
            _init_row = row if not is_empty_row and not _init_row else _init_row

            # Define final table row if not defined and current row is empty
            _last_row = row - 1 if is_empty_row and _init_row else _last_row

            if _init_row and _last_row:
                tables.append(((initial_col, _init_row), (last_col, _last_row)))
                _init_row = None
                _last_row = None

            if _init_row and row == last_row:
                tables.append(((initial_col, _init_row), (last_col, row)))

        return tables

    def _find_empty_columns(self, initial: bool = False):
        tables = self._find_empy_rows()
        final_tables = []
        for t in tables:
            initial_col = t[0][0]
            final_col = t[1][0]

            initial_row = t[0][1]
            final_row = t[1][1]

            _init_col = None
            _last_col = None

            for col in range(initial_col, final_col + 1):
                coordinates = None
                values = [
                    item["value"]
                    for item in filter(
                        lambda item: item["y"] == col
                        and item["x"] in range(initial_row, final_row + 1),
                        self.data_list,
                    )
                ]
                empty_col = self._all_false(values)

                _init_col = col if not empty_col and not _init_col else _init_col
                _last_col = col - 1 if empty_col and _init_col else _last_col

                if _init_col and _last_col:
                    coordinates = (
                        (_init_col, initial_row),
                        (_last_col, final_row),
                    )
                    _init_col = None
                    _last_col = None

                if _init_col and col == final_col + 1:
                    coordinates = ((_init_col, initial_row), (col, final_row))

                if coordinates and not coordinates[0] == coordinates[1]:
                    final_tables.append(coordinates)

        return final_tables

    def check_orientation(self, values: List[str], headers: bool = False) -> bool:
        len_col = len(values)
        acceptable_value = len_col
        if acceptable_value % 1 < 0.5:
            acceptable = math.floor(acceptable_value)
        else:
            acceptable = math.ceil(acceptable_value)
        # print("values", values)
        # print("acceptable", acceptable)
        # acceptable = int(len_col * 0.)
        col_type = {
            "is_int": 0,
            "is_float": 0,
            "is_date": 0,
            "is_null": 0,
            "is_empty": 0,
            "is_str": 0,
        }
        for cell in values:
            cell_type = self.get_value_type(self.clean_is_empty(cell))
            col_type["is_int"] += cell_type.is_int
            col_type["is_float"] += cell_type.is_float
            col_type["is_date"] += cell_type.is_date
            col_type["is_str"] += cell_type.is_str
            # col_type["is_empty"] += cell_type.is_empty
            if headers:
                col_type["is_str"] += cell_type.is_str

        # print("col_type", col_type)

        if headers and col_type["is_str"] >= acceptable:
            return True

        for key, value in col_type.items():
            if value >= acceptable:
                return True

        return False

    def process_matrix(self):
        table_coordinates = self._find_empty_columns()
        final_matrix = []
        result = None
        final_tables = []
        for table in table_coordinates:
            # check if table has headers
            table_init = table[0]
            table_end = table[1]
            row_init = table_init[1]
            column_init = table_init[0]

            row_end = table_end[1]
            column_end = table_end[0]

            values_to_check = []

            # Single row or column, not a table
            if row_init == row_end or column_init == column_end:
                continue

            """
            Check row orientation
            row = numbers = x
            Let's remove the first column then evaluate three rows
            wether removing the first column there is no any row we pop the table since it is a single row, not a table
            wether every row has the same type of values we might assume the table is row-oriented
            """

            row_types = []
            for row in range(row_init, row_init + 3):
                values = [
                    item["value"]
                    for item in filter(
                        lambda item: item["x"] == row
                        and item["y"] in range(column_init + 1, column_end + 1),
                        self.data_list,
                    )
                ]
                print("values row ", values)
                orientation = self.check_orientation(values)
                print("orientation row ", orientation)
                row_types.append(orientation)

            """
            Check column orientation
            column = letters = y
            Let's apply the same logic: remove the first row and evaluate every column type values
            """
            col_types = []
            for col in range(column_init, column_init + 3):
                values = [
                    item["value"]
                    for item in filter(
                        lambda item: item["y"] == col
                        and int(item["x"]) in range(row_init + 1, row_end + 1),
                        self.data_list,
                    )
                ]
                print("values col ", values)
                orientation_col = self.check_orientation(values)
                print("orientation col ", orientation_col)
                col_types.append(orientation_col)

            """
            Evaluate orientation
            wether the table is both, row and column-oriented, we cannot determine the orientatation
            """
            row_oriented = all(row_types)
            col_oriented = all(col_types)

            """
            Find headers
            Let's evalueate the first row or column, depending of the orientation, to find possible headers
            """

            final_tables += self.get_table_data(table, row_oriented, col_oriented)

        return final_tables

    def get_table_data(self, table, row_oriented, col_oriented):
        table_init = table[0]
        table_end = table[1]
        row_init = table_init[1]
        column_init = table_init[0]

        row_end = table_end[1]
        column_end = table_end[0]

        headers = []

        possibles_data = []

        if row_oriented and not col_oriented:
            headers = [
                item["value"]
                for item in filter(
                    lambda item: item["y"] == column_init
                    and int(item["x"]) in range(row_init, row_end + 1),
                    self.data_list,
                )
            ]

        if not row_oriented and col_oriented:
            headers = [
                item["value"]
                for item in filter(
                    lambda item: item["x"] == row_init
                    and int(item["y"]) in range(column_init, column_end + 1),
                    self.data_list,
                )
            ]

        print("headers", headers)

        if col_oriented:
            _data = []
            r_init = row_init + 1 if headers else row_init
            for row in range(r_init, row_end + 1):
                _doc = {}
                n = 0
                for col in range(column_init, column_end + 1):
                    value = list(
                        filter(
                            lambda item: item["x"] == row and item["y"] == col,
                            self.data_list,
                        )
                    )[0]["value"]
                    header = headers[n] if headers else f"column_{n}"

                    _doc[header] = value
                    n += 1
                _data.append(_doc)
            possibles_data.append({"headers": list(_data[0].keys()), "data": _data})

        if row_oriented:
            _data = []
            c_init = column_init + 1 if headers else column_init
            for col in range(c_init, column_end + 1):
                _doc = {}
                n = 0
                for row in range(row_init, row_end + 1):
                    value = list(
                        filter(
                            lambda item: item["x"] == row and item["y"] == col,
                            self.data_list,
                        )
                    )[0]["value"]
                    header = headers[n] if headers else f"column_{n}"
                    print(header, value)
                    _doc[header] = value
                    n += 1
                _data.append(_doc)
            possibles_data.append({"headers": list(_data[0].keys()), "data": _data})

        return possibles_data
