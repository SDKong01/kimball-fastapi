import io
import csv
import json
import zipfile
import pandas as pd
from typing import List
from tempfile import SpooledTemporaryFile, TemporaryFile
from starlette.datastructures import UploadFile

from src.domain.data_source.exceptions import InvalidFormatException
from src.domain.data_source.services import DataSourceServices


class DataSourceAppServices:

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
            "xlsx": self.process_xls,
            "zip": self.process_zip,
        }
        return parsers[format]

    def _file_name(self, file_name: str) -> str:
        full_filename = file_name
        file_name = full_filename.split(".")[:-1]
        file_name = " ".join(file_name)
        return file_name

    def upload_file(self, file: UploadFile):
        file_format = self._file_format(file.filename)
        parser = self._get_file_parser(file_format)
        data_parsed = parser(file.file)
        file_name = self._file_name(file.filename)
        repo = DataSourceServices.get_repo(collection=file_name)
        n_items = repo.insert_many(data_parsed)
        return len(n_items)
