from abc import ABC, abstractmethod
from typing import Any, Dict, Union


class AbstractBSONFactory(ABC):
    @abstractmethod
    def insert_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Retrieve a BSON query to insert a document.

        :param data: A dictionary with the data to insert.
        :return: A BSON query dict.
        """
        pass

    @abstractmethod
    def update_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Retrieve a BSON query to update a document.

        :param data: A dictionary with the data to update.
        :return: A BSON query dict.
        """
        pass

    @abstractmethod
    def insert_many(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Retrieve a BSON query to insert multiple documents.

        :param data: A dictionary with the data to insert.
        :return: A BSON query dict.
        """
        pass

    @abstractmethod
    def find_one(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Retrieve a BSON query to find a document.

        :param data: A dictionary with the data to find.
        :return: A BSON query dict.
        """
        pass

    @abstractmethod
    def find(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Retrieve a BSON query to find multiple documents.

        :param data: A dictionary with the data to find.
        :return: A BSON query dict.
        """
        pass
