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
from abc import ABC, abstractmethod


@dataclass
class DataSetDTO:
    data: List[Dict[str, Any]]
    collection_name: str


class ProcesorBase(ABC):
    def __init__(self, uploadfile: UploadFile):
        self.uploadfile = uploadfile
        self.file: SpooledTemporaryFile = uploadfile.file

    def coll_name(self) -> str:
        full_filename = self.uploadfile.filename
        file_name = full_filename.split(".")[:-1]
        file_name = " ".join(file_name)
        return f"temp_{file_name}"

    @abstractmethod
    def process(self) -> Tuple[DataSetDTO]:
        pass


class CSVProcesor(ProcesorBase):
    def process(self) -> Tuple[DataSetDTO]:
        content = self.file.read().decode("utf-8").splitlines()
        reader = list(csv.DictReader(content))
        response = DataSetDTO(data=reader, collection_name=self.coll_name())
        return (response,)


class JSONProcesor(ProcesorBase):
    def process(self) -> Tuple[DataSetDTO]:
        content = self.file.read().decode("utf-8")
        data = json.loads(content)
        response = DataSetDTO(data=data, collection_name=self.coll_name())
        return (response,)


class XLSProcesor(ProcesorBase):
    def process(self, file: SpooledTemporaryFile) -> Tuple[DataSetDTO]:
        df = pd.read_excel(file)
        data = df.to_dict(orient='records')
        response = DataSetDTO(data=data, collection_name=self.coll_name())
        return (response,)


class XLSXProcesor(ProcesorBase):
    def _excel_columns(self) -> List[str]:
        columns = []
        for letter in string.ascii_uppercase:
            columns.append(letter)
        for first_letter in string.ascii_uppercase:
            for second_letter in string.ascii_uppercase:
                columns.append(first_letter + second_letter)
        return columns

    def split_numbers_and_letters(self, s: str) -> Tuple[str, str]:
        numbers = ''.join([char for char in s if char.isdigit()])
        letters = ''.join([char for char in s if char.isalpha()])
        return (numbers, letters)

    def process(self) -> Tuple[DataSetDTO]:
        workbook = load_workbook(self.file)
        sheets = workbook.sheetnames
        data = []
        response = []
        for s in sheets:
            sheet = workbook[s]
            data = []
            data = [
                {
                    "x": int(self.split_numbers_and_letters(cell.coordinate)[0]),
                    "y": self._excel_columns().index(
                        self.split_numbers_and_letters(cell.coordinate)[1]
                    ),
                    "column": self.split_numbers_and_letters(cell.coordinate)[1],
                    "row": int(self.split_numbers_and_letters(cell.coordinate)[0]),
                    "value": cell.value,
                    "id": cell.coordinate,
                }
                for row in sheet.iter_rows()
                for cell in row
            ]
            response.append(DataSetDTO(data=data, collection_name=f"temp_{s}"))

        return tuple(response)


class FileServices:
    def __init__(self):
        pass

    ### -------------------- File Upload --------------------
    def _file_format(self, file_name: str) -> str:
        valid_extensions = ["csv", "json", "xls", "xlsx", "zip"]
        extension = file_name.split(".")[-1]
        if extension not in valid_extensions:
            raise InvalidFormatException(item="file", detail="Invalid file format")
        return extension

    # def process_zip(self, file: SpooledTemporaryFile) -> List[dict]:
    #     data = []
    #     with zipfile.ZipFile(file, 'r') as zip_ref:
    #         for f in zip_ref.namelist():
    #             try:
    #                 file_format = self._file_format(f)
    #                 parser = self._get_file_parser(file_format)
    #                 file_bytes = zip_ref.read(f)
    #                 file_io = io.BytesIO(file_bytes)
    #                 _data = parser(file_io)
    #                 data += _data
    #             except:
    #                 continue
    #     return data

    available_formats = ["csv", "json", "xls", "xlsx"]

    format_processors: Dict[str, ProcesorBase] = {
        "csv": CSVProcesor,
        "json": JSONProcesor,
        "xls": XLSProcesor,
        "xlsx": XLSXProcesor,
    }

    def _instatiate_processor(self, file: UploadFile) -> ProcesorBase:
        file_format = self._file_format(file.filename)
        if not file_format:
            raise InvalidFormatException(
                item="file",
                detail="Invalid file format. Only csv, json, xls, xlsx, zip are allowed",
            )
        processor = self.format_processors.get(file_format, CSVProcesor)(file)
        return processor

    def upload_file(self, file: UploadFile) -> List[str]:
        processor = self._instatiate_processor(file)
        datasets = processor.process()
        data_services = DatasetServices()
        created = []

        for dt in datasets:
            data_services.create_only_data(
                data=dt.data, collection_name=dt.collection_name
            )
            created.append({"sheet": dt.collection_name, "data": dt.data})

        return created
