from openpyxl import load_workbook
from itertools import count

from src.domain.dataset.services import DatasetServices

import uuid
from os import getenv
from os import environ
from nest.core.app import App
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.mongo_manager.mongo_db_connection import MongoDBConnection

from src.interface.data_source.module import DataSourceModule

from src.interface.discovery_engine.module import DiscoveryEngineModule
from src.interface.connection.module import ConnectionModule
from src.interface.queryset.module import QuerySetModule
from src.interface.dataset.module import DatasetModule

from src.domain.connection.models import ConnParams

from src.domain.connection.services import ConnServices
from src.config import settings
import logging


def main():
    filepath = "/home/alan/Kainam/datasets/tree_gs.xlsx"
    wb = load_workbook(filepath)
    layout = wb['Layout']
    n: count = count()
    nodes = []
    ds = DatasetServices()
    created = 0
    for row in layout.iter_rows(values_only=True, min_row=2):
        node = {
            "id_centro_costos": row[0],
            "nombre": row[1],
            "id_config": row[2],
            "id_grupo_empresarial": row[3],
            "descripcion_grupo_empresarial": row[4],
            "id_entidad": row[5],
            "entidad": row[6],
            "parent_id": row[7],
            "segmento_canal": row[8],
            "status": row[9],
            "tipo_operacion": row[10],
            "colonia": row[11],
            "estado": row[12],
            "municipio": row[13],
            "localidad": row[14],
            "codigo_postal": row[15],
            "pais": row[16],
            "tipo_cc": row[17],
            "color": row[18],
        }
        nodes.append(node)

        if (created := next(n)) % 5000 == 0:
            ds.create_only_data(nodes, "tree_gs")
            nodes = []
            print(f"{created*5000} rows inserted")

    ds.create_only_data(nodes, "tree_gs")
    print("Done")


if __name__ == '__main__':
    db_params = ConnParams(
        engine="mongodb",
        params={
            "host": settings.MONGO_HOST,
            "username": settings.MONGO_USER,
            "password": settings.MONGO_PASS,
            "port": settings.MONGO_PORT,
            "is_atlas_cluster": settings.MONGO_IS_ATLAS_CLUSTER,
            # "database": settings.MONGO_DB,
        },
    )
    connector = ConnServices.open_persistant_connection(db_params)
    settings.db_client_connector = connector
    settings.db_client_params = ConnParams(
        id=connector.id, engine=db_params.engine, params=db_params.params
    )
    main()
