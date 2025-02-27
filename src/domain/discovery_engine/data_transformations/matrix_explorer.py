import re
import math
import string
from itertools import groupby
from collections import Counter, defaultdict
from dateutil.parser import parse
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Type, Any

from dataclasses import dataclass
from src.domain.boxtool.services import Services as BoxToolServices


@dataclass
class CellType:
    is_int: Optional[bool]
    is_float: Optional[bool]
    is_bool: Optional[bool]
    is_date: Optional[bool]
    is_str: Optional[bool]
    is_null: Optional[bool]
    is_empty: Optional[bool]

    def __repr__(self):
        types = []
        if self.is_int:
            types.append("int")
        if self.is_float:
            types.append("float")
        if self.is_bool:
            types.append("bool")
        if self.is_date:
            types.append("date")
        if self.is_str:
            types.append("str")
        if self.is_null:
            types.append("null")
        if self.is_empty:
            types.append("empty")
        return f"CellType({', '.join(types)})"


class CellTypeFactory:
    def __init__(self, value: Any):
        self.value = value

    def clean_is_empty(self, value: str) -> bool:
        null_values = ["", " ", "null", "nan", "none"]
        if value.lower() in null_values:
            return True
        return False

    def _is_date(self) -> bool:
        date_pattern = r'\b(\d{4}[-/]\d{2}(?:[-/]\d{2})?(?:[T\s]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?)?|\d{2}[-/]\d{2}[-/]\d{4})\b'
        if re.match(date_pattern, str(self.value)):
            return True
        return False

    def compute(self) -> CellType:
        value = str(self.value).strip()
        is_empty = self.clean_is_empty(value)

        cell_type = CellType(
            is_int=value.isdigit(),
            is_float=value.replace(".", "", 1).isdigit() and "." in value,
            is_date=self._is_date(),
            is_null=None == value,
            is_empty=is_empty,
            is_str=bool(not is_empty and not value.isdigit()),
            is_bool=value.lower() in {"true", "false", "1", "0"},
        )
        return cell_type


@dataclass
class Cell:
    x: int
    y: int
    value: Any
    celltype: CellType


class MatrixExplorerTransformations:
    def __init__(self, data: Dict[str, Dict[str, str]]):
        # self.data = data
        self.data_list = data
        self.cell_profiles: Dict[str, Dict[str, str]] = {}
        self.data_map = defaultdict(lambda: defaultdict(lambda: None))
        self.excel_data_map = defaultdict(lambda: defaultdict(lambda: None))
        try:
            for item in self.data_list:
                self.data_map[item["y"]][item["x"]] = item["value"]
                self.excel_data_map[item["column"]][item["row"]] = item["value"]
        except Exception as e:
            pass

    @dataclass
    class CellProfile:
        header: Optional[float] = None
        table: Optional[float] = None
        column: Optional[float] = None
        value_type: Optional[str] = None
        is_null: Optional[bool] = False
        is_index: Optional[float] = None

    @dataclass
    class TableData:
        columns_type = List[Any]
        headers = List[str]
        raw_data = List[Any]

    # def _is_date(self, value: str) -> bool:
    #     date_pattern = r'\b(\d{4}[-/]\d{2}(?:[-/]\d{2})?(?:[T\s]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?)?|\d{2}[-/]\d{2}[-/]\d{4})\b'
    #     if re.match(date_pattern, value):
    #         return True
    #     return False
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

    # def clean_is_empty(self, value: str) -> bool:
    #     null_values = ["", " ", "null", "nan", "none", "None"]
    #     if value and str(value).lower() in null_values:
    #         return None
    #     return value

    # def get_value_type(self, value: str) -> CellType:
    #     str_value = str(value)
    #     cell_type = self.CellType(
    #         is_int=bool(value and str_value.isdigit()),
    #         is_float=bool(value and str_value.replace(".", "", 1).isdigit()),
    #         is_date=bool(value and self._is_date(str_value)),
    #         is_null=None == value,
    #         is_empty=bool(value and self.clean_is_empty(str_value)),
    #         is_str=bool(value and not str_value.isdigit()),
    #         is_bool=bool(value and str_value.lower() in ["true", "false", "1", "0"]),
    #     )

    #     return cell_type

    # class Cell:
    #     def __init__(self):
    #         self.row_condition: None
    #         self.coll_condidtion: None
    #         self.prev_rows: None
    #         self.prev_cols: None
    #         x: 0
    #         y: 0
    #         is_row_oriented: True
    #         is_col_oriented: True

    def orientation(self, x: int, y: int, x_end: int, y_end: int) -> Tuple[int, int]:
        print()
        full_table_data = [
            Cell(
                x=item["x"],
                y=item["y"],
                value=item["value"],
                celltype=CellTypeFactory(item["value"]).compute(),
            )
            # ((item["x"], item["y"]), item)
            for item in self.data_list
            if item["x"] in range(x + 1, x_end) and item["y"] in range(y + 1, y_end)
        ]
        data_sorted = sorted(
            full_table_data,
            key=lambda d: d.y,
        )

        prev_x, prev_y = None, None
        # prev_x_cells: List[CellType] = []
        # prev_y_cells: List[CellType] = []

        prev_x_cells: List[Cell] = []
        prev_y_cells: List[Cell] = []

        is_x_oriented, is_y_oriented = True, True

        def ignore_nones(
            x: CellType, y: Cell, to_print: bool = False, _x: Any = None
        ) -> bool:
            if to_print:
                print("**************** x *********************")
                print(_x, x)
                print("**************** y *********************")
                print(y)
            return x == y.celltype if not y.celltype.is_null else True

        for cell in data_sorted:
            # Table begin
            if not prev_x and not prev_y:
                prev_x, prev_y = cell.x, cell.y
                continue

            # Not orientation founded, break the loop
            if not is_x_oriented and not is_y_oriented:
                is_y_oriented, is_x_oriented = True, True
                print("not orientation found")
                break

            is_y_different = cell.x != prev_x
            is_x_different = cell.y != prev_y

            if is_y_different and is_x_different:
                prev_x_cells = []
                prev_y_cells = []

            if is_x_different and is_x_oriented:
                is_x_oriented = all(
                    ignore_nones(p.celltype, cell) for p in prev_x_cells
                )
                prev_x_cells = []

            if is_y_different and is_y_oriented:
                print(
                    "y different",
                    list(prev_y_cells),
                )
                print()
                is_y_oriented = all(
                    ignore_nones(p.celltype, cell, True, (p.x, p.y))
                    for p in prev_y_cells
                )
                prev_y_cells = []

            prev_x_cells.append(cell)
            prev_y_cells.append(cell)
            prev_x, prev_y = cell.x, cell.y

        return is_x_oriented, is_y_oriented

    # def get_value_type(self, value: str) -> CellType:
    #     value = str(value).strip()
    #     is_empty = bool(value and self.clean_is_empty(str(value)))

    #     cell_type = CellType(
    #         is_int=value.isdigit(),
    #         is_float=value.replace(".", "", 1).isdigit() and "." in value,
    #         is_date=self._is_date(value),
    #         is_null=None == value,
    #         is_empty=is_empty,
    #         is_str=bool(not is_empty and not value.isdigit()),
    #         is_bool=value.lower() in {"true", "false", "1", "0"},
    #     )
    #     return cell_type

    def _all_false(self, iterable) -> bool:
        return all(not element for element in iterable)

    from collections import Counter

    # def check_orientation(
    #     self, values: List[str], headers: bool = False, to_print: bool = False
    # ) -> bool:
    #     if to_print:
    #         print("values pre clean empty check orientation", values)
    #     values = [self.clean_is_empty(v) for v in values]  # Limpiar primero
    #     if to_print:
    #         print("values after check_orientation", values)
    #     acceptable = round(len(values))  # Evita `math.floor` o `math.ceil`
    #     col_type = Counter()

    #     for cell in values:
    #         cell_type = self.get_value_type(cell)
    #         col_type["is_int"] += cell_type.is_int
    #         col_type["is_float"] += cell_type.is_float
    #         col_type["is_date"] += cell_type.is_date
    #         col_type["is_str"] += cell_type.is_str or headers  # Simplificado
    #     if to_print:
    #         print("vales after for in check_orientation", col_type)
    #     return any(value >= acceptable for value in col_type.values())

    # from collections import defaultdict

    # def process_matrix(self, has_headers: bool = False):
    #     box_services = BoxToolServices(self.data_list)
    #     new_coordinates = box_services.execute()
    #     final_tables = []
    #     for table in new_coordinates:
    #         # check if table has headers
    #         table_init = table[0]
    #         table_end = table[1]
    #         row_init = table_init[1]
    #         column_init = table_init[0]

    #         row_end = table_end[1]
    #         column_end = table_end[0]

    #         # Single row or column, not a table
    #         if row_init == row_end or column_init == column_end:
    #             continue

    #         """
    #         Check row orientation
    #         row = numbers = x
    #         Let's remove the first column then evaluate three rows
    #         wether removing the first column there is no any row we pop the table since it is a single row, not a table
    #         wether every row has the same type of values we might assume the table is row-oriented
    #         """

    #         row_types = []
    #         for row in range(row_init, row_init + 3):
    #             values = {
    #                 item["value"]
    #                 for item in self.data_list
    #                 if item["y"] == row
    #                 and item["x"] in range(column_init + 1, column_end + 1)
    #             }

    #             orientation = self.check_orientation(values)
    #             row_types.append(orientation)
    #         print(row_types)

    #         """
    #         Check column orientation
    #         column = letters = y
    #         Let's apply the same logic: remove the first row and evaluate every column type values
    #         """
    #         col_types = []
    #         for col in range(column_init, column_init + 3):
    #             values = {
    #                 item["value"]
    #                 for item in self.data_list
    #                 if item["x"] == col
    #                 and item["y"] in range(row_init + 1, row_end + 1)
    #             }
    #             orientation_col = self.check_orientation(values)
    #             col_types.append(orientation_col)

    #         """
    #         Evaluate orientation
    #         wetherCellType the table is both, row and column-oriented, we cannot determine the orientatation
    #         """
    #         row_oriented = all(row_types)
    #         col_oriented = all(col_types)

    #         """
    #         Find headers
    #         Let's evalueate the first row or column, depending of the orientation, to find possible headers
    #         """
    #         # print(table)
    #         final_tables += self.get_table_data(
    #             table, row_oriented, col_oriented, has_headers
    #         )

    #     return final_tables

    def process_matrix(self, has_headers: bool = False):
        box_services = BoxToolServices(self.data_list)
        new_coordinates = box_services.execute()
        final_tables = []

        # Crear estructura de datos para acceso rápido
        # data_map = defaultdict(lambda: defaultdict(lambda: None))
        # for item in self.data_list:
        #     data_map[item["y"]][item["x"]] = item["value"]

        # def evaluate_orientation(start, end, fixed, is_row):
        #     if is_row:
        #         print(start, end, fixed)
        #     """Evalúa la orientación de filas o columnas."""
        #     orientations = []

        #     value = lambda index, pos: (
        #         self.data_map[index][pos] if is_row else self.data_map[pos][index]
        #     )

        #     for index in range(start, max(start + 5, end)):
        #         values = (
        #             self.data_map[index][pos] if is_row else self.data_map[pos][index]
        #             for pos in range(fixed + 1, end + 1)
        #             if self.data_map[index][pos] is not None
        #         )
        #         # if is_row:
        #         #     print("values: ", list(values))
        #         orientations.append(self.check_orientation(values, to_print=is_row))
        #     if is_row:
        #         print("orientations, ", orientations)
        #     return all(orientations)

        for table in new_coordinates:
            print("new coordinates", table)
            (column_init, row_init), (column_end, row_end) = table

            # A single line or single columns, not a table
            if row_init == row_end or column_init == column_end:
                continue

            row_oriented, col_oriented = self.orientation(
                x=row_init, y=column_init, x_end=row_end, y_end=column_end
            )

            # row_oriented = evaluate_orientation(
            #     row_init, row_end, column_init, is_row=True
            # )
            # col_oriented = evaluate_orientation(
            #     column_init, column_end, row_init, is_row=False
            # )

            # if not col_oriented and not row_oriented:
            #     col_oriented, row_oriented = True, True

            final_tables += self.get_table_data(
                table, row_oriented, col_oriented, has_headers
            )
        return final_tables

    def parse_cols_rows(self, _range: str):
        match = re.match(r'^([A-Z]+)([0-9]+):([A-Z]+)([0-9]+)$', _range)
        if not match:
            return None, None
        # print(match.groups())
        col_inicio, fila_inicio, col_fin, fila_fin = match.groups()
        columnas = self.generate_range_columns(col_inicio, col_fin)
        # print("columnas", columnas)
        fila_inicio = int(fila_inicio)
        fila_fin = int(fila_fin)
        filas = list(range(fila_inicio, fila_fin + 1))

        return columnas, filas

    def generate_range_columns(self, col_inicio, col_fin):
        """Transform Excel column in numbers and generate letters range"""

        def columna_a_num(col):
            # Transfor a column (ej. 'A', 'Z', 'AA') in a number
            num = 0
            for char in col:
                num = num * 26 + (ord(char) - ord('A') + 1)
            return num

        def num_a_columna(num):
            # (ej. 1 -> 'A', 27 -> 'AA')
            col = ""
            while num > 0:
                num -= 1
                col = chr(num % 26 + ord('A')) + col
                num //= 26
            return col

        num_inicio = columna_a_num(col_inicio)
        num_fin = columna_a_num(col_fin)

        return [num_a_columna(n) for n in range(num_inicio, num_fin + 1)]

    def get_raw_data_by_range(self, cell_range: str = None, has_headers: bool = True):
        if cell_range:
            cols, rows = self.parse_cols_rows(cell_range)
        else:
            cols = sorted({d["column"] for d in self.data_list})
            rows = sorted({d["row"] for d in self.data_list})
        filtered_data = []
        for r in rows:
            row_data = {"row": r}
            row_data.update({c: self.excel_data_map[c][r] for c in cols})
            filtered_data.append(row_data)
        return filtered_data

    # def get_table_data(self, table, row_oriented, col_oriented, has_headers: bool):
    #     table_init, table_end = table
    #     column_init, row_init = table_init
    #     column_end, row_end = table_end

    #     # 🔹 Construir un diccionario para acceso rápido en O(1)
    #     # data_map = defaultdict(lambda: defaultdict(lambda: None))
    #     # for item in self.data_list:
    #     #     data_map[item["y"]][item["x"]] = item["value"]

    #     headers = []
    #     possibles_data = []

    #     # 🔹 Calcular headers solo una vez
    #     if has_headers:
    #         headers = [
    #             (
    #                 self.data_map[y][column_init]
    #                 if row_oriented
    #                 else self.data_map[row_init][x]
    #             )
    #             for y in range(row_init, row_end + 1)
    #             if row_oriented
    #             for x in range(column_init, column_end + 1)
    #             if col_oriented
    #         ]

    #     # 🔹 Función para obtener el header de una columna, si no existe, generar uno genérico
    #     def get_header(index):
    #         return headers[index] if headers else f"column_{index}"

    #     # 🔹 Procesar datos según orientación
    #     def process_orientation(is_col_oriented):
    #         _init = (
    #             (row_init + 1 if has_headers else row_init)
    #             if is_col_oriented
    #             else (column_init + 1 if has_headers else column_init)
    #         )

    #         range_x = (
    #             range(column_init, column_end + 1)
    #             if is_col_oriented
    #             else range(_init, column_end + 1)
    #         )
    #         range_y = (
    #             range(_init, row_end + 1)
    #             if is_col_oriented
    #             else range(row_init, row_end + 1)
    #         )
    #         # Obtener datos filtrados
    #         filtered_data = [
    #             {"x": x, "y": y, "value": self.data_map[y][x]}
    #             for x in range_x
    #             for y in range_y
    #             if self.data_map[y][x] is not None
    #         ]
    #         # Ordenar por la clave correcta (y si es col_oriented, x si no)
    #         sorted_data = sorted(
    #             filtered_data, key=lambda d: d["y"] if is_col_oriented else d["x"]
    #         )
    #         # Agrupar por la misma clave
    #         grouped_data = [
    #             list(group)
    #             for _, group in groupby(
    #                 sorted_data, key=lambda d: d["y"] if is_col_oriented else d["x"]
    #             )
    #         ]

    #         # Convertir a formato de tabla
    #         data_table = [
    #             {get_header(idx): item["value"] for idx, item in enumerate(group)}
    #             for group in grouped_data
    #         ]

    #         possibles_data.append(
    #             {"headers": list(data_table[0].keys()), "data": data_table}
    #         )

    #     if col_oriented:
    #         process_orientation(True)
    #     if row_oriented:
    #         process_orientation(False)

    #     return possibles_data

    def get_table_data(self, table, row_oriented, col_oriented, has_headers: bool):
        table_init, table_end = table
        column_init, row_init = table_init
        column_end, row_end = table_end

        headers = []
        possibles_data = []

        if row_oriented and not col_oriented:
            headers = [
                item["value"]
                for item in filter(
                    lambda item: item["y"] in range(row_init, row_end + 1)
                    and item["x"] == column_init,
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

        header = lambda x: headers[x] if headers else f"column_{x}"
        y = lambda x: x - row_init
        x = lambda y: y - column_init

        if col_oriented:
            _row_init = row_init + 1 if has_headers else row_init
            full_table_data = [
                item
                for item in self.data_list
                if item["x"] in range(column_init, column_end + 1)
                and item["y"] in range(_row_init, row_end + 1)
            ]
            _data_sorted = sorted(
                full_table_data,
                key=lambda d: d["y"],
            )
            grouped_data = [
                tuple(group) for _, group in groupby(_data_sorted, key=lambda d: d["y"])
            ]

            _data = [
                {header(x(item["x"])): item["value"] for item in col_axis}
                for col_axis in grouped_data
            ]
            possibles_data.append({"headers": list(_data[0].keys()), "data": _data})

        if row_oriented:
            _col_init = column_init + 1 if has_headers else column_init
            full_table_data = [
                item
                for item in self.data_list
                if item["x"] in range(_col_init, column_end + 1)
                and item["y"] in range(row_init, row_end + 1)
            ]
            _data_sorted = sorted(
                full_table_data,
                key=lambda d: d["x"],
            )
            grouped_data = [
                tuple(group) for _, group in groupby(_data_sorted, key=lambda d: d["x"])
            ]
            _data = [
                {header(y(item["y"])): item["value"] for item in col_axis}
                for col_axis in grouped_data
            ]

            possibles_data.append({"headers": list(_data[0].keys()), "data": _data})

        return possibles_data
