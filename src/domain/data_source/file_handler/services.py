import io
import csv
import json
import string
import zipfile
import pandas as pd
from typing import List, Optional, Dict, Union, Any, Tuple
from tempfile import SpooledTemporaryFile, TemporaryFile
from starlette.datastructures import UploadFile
from dataclasses import dataclass
from dataclass_type_validator import dataclass_validate
from src.domain.data_source.exceptions import (
    InvalidFormatException,
    DBEngineNotSupported,
)

# from src.domain.connection.queryset import QuerySet
from src.config import settings
from openpyxl import load_workbook, Workbook
from src.domain.dataset.services import DatasetServices


class FileServices:
    def __init__(self):
        self.our = None
        # self.our_db = QuerySet(db_manager=settings.db_client)

    ### -------------------- File Upload --------------------
    def _file_format(self, file_name: str) -> str:
        valid_extensions = ["csv", "json", "xls", "xlsx", "zip"]
        extension = file_name.split(".")[-1]
        if extension not in valid_extensions:
            raise InvalidFormatException(item="file", detail="Invalid file format")
        return extension

    def process_csv(self, file: SpooledTemporaryFile) -> List[dict]:
        content = file.read().decode("utf-8").splitlines()
        reader = list(csv.DictReader(content))
        return reader

    def process_json(self, file: SpooledTemporaryFile) -> List[dict]:
        content = file.read().decode("utf-8")
        data = json.loads(content)
        return data

    def process_xls(self, file: SpooledTemporaryFile) -> List[dict]:
        df = pd.read_excel(file)
        data = df.to_dict(orient='records')
        return data

    def split_numbers_and_letters(self, s: str) -> Tuple[str, str]:
        numbers = ''.join([char for char in s if char.isdigit()])
        letters = ''.join([char for char in s if char.isalpha()])
        return (numbers, letters)

    def _excel_columns(self) -> List[str]:
        columns = []
        for letter in string.ascii_uppercase:
            columns.append(letter)
        for first_letter in string.ascii_uppercase:
            for second_letter in string.ascii_uppercase:
                columns.append(first_letter + second_letter)
        return columns

    def process_xlsx(self, file: SpooledTemporaryFile) -> List[dict]:
        workbook = load_workbook(file)
        sheet = workbook.active
        data = []
        # last_row = sheet.max_row
        # last_column = sheet.max_column

        for row in sheet.iter_rows():
            for cell in row:
                x, y = self.split_numbers_and_letters(cell.coordinate)
                data.append(
                    {
                        "x": int(x),
                        "y": self._excel_columns().index(y),
                        "value": cell.value,
                        "id": cell.coordinate,
                    }
                )
                # print(f"Celda: {cell.coordinate}, Valor: {cell.value}")
                # break
        return data

    def process_zip(self, file: SpooledTemporaryFile) -> List[dict]:
        data = []
        with zipfile.ZipFile(file, 'r') as zip_ref:
            for f in zip_ref.namelist():
                try:
                    file_format = self._file_format(f)
                    parser = self._get_file_parser(file_format)
                    file_bytes = zip_ref.read(f)
                    file_io = io.BytesIO(file_bytes)
                    _data = parser(file_io)
                    data += _data
                except:
                    continue
        return data

    def _get_file_parser(self, format: str) -> callable:
        parsers = {
            "csv": self.process_csv,
            "json": self.process_json,
            "xls": self.process_xls,
            "xlsx": self.process_xlsx,
            "zip": self.process_zip,
        }
        return parsers[format]

    def _file_name(self, file_name: str) -> str:
        full_filename = file_name
        file_name = full_filename.split(".")[:-1]
        file_name = " ".join(file_name)
        return file_name

    def upload_file(self, file: UploadFile, db: str) -> int:
        file_format = self._file_format(file.filename)
        parser = self._get_file_parser(file_format)
        data_parsed = parser(file.file)
        file_name = self._file_name(file.filename)
        data_services = DatasetServices()
        data_services.create_only_data(data=data_parsed, collection_name=file_name)
        # self.clone_to_self_db(collection_dest=file_name, db_dest=db, data=data_parsed)
        return len(data_parsed)

    # def clone_to_self_db(
    #     self,
    #     collection_dest: str,
    #     db_dest: str,
    #     data: Union[Dict[str, Any], Dict[str, Any], None] = None,
    # ):
    #     self.our_db.db_manager.collection = collection_dest
    #     self.our_db.db_manager.db = db_dest
    #     self.our_db.insert_many(data)
