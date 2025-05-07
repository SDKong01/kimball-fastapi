import os
import io
import sys
import traceback
import psycopg2
import subprocess
import datetime
import multiprocessing
from dotenv import load_dotenv

from datetime import datetime, timedelta
from functools import wraps
from typing import Callable
from contextlib import contextmanager
from time import time
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map


load_dotenv()

# DB origin details
DB_ORIGIN = os.getenv("DB_ORIGIN")
USER_ORIGIN = os.getenv("USER_ORIGIN")
HOST_ORIGIN = os.getenv("HOST_ORIGIN")
PORT_ORIGIN = os.getenv("PORT_ORIGIN")
PASS_ORIGIN = os.getenv("PASS_ORIGIN")
SCHEMA_ORIGIN = os.getenv("SCHEMA_ORIGIN")
FULL_CONN_ORIGIN = {
    "dbname": DB_ORIGIN,
    "user": USER_ORIGIN,
    "password": PASS_ORIGIN,
    "host": HOST_ORIGIN,
    "port": PORT_ORIGIN,
}

# DB destination details
DB_DEST = os.getenv("DB_DEST")
USER_DEST = os.getenv("USER_DEST")
HOST_DEST = os.getenv("HOST_DEST")
PORT_DEST = os.getenv("PORT_DEST")
PASS_DEST = os.getenv("PASS_DEST")
SCHEMA_DEST = os.getenv("SCHEMA_DEST")
FULL_CONN_DEST = {
    "dbname": DB_DEST,
    "user": USER_DEST,
    "password": PASS_DEST,
    "host": HOST_DEST,
    "port": PORT_DEST,
}


TABLE_NAME = "table"
QUERY = "where executed_at > '2025-04-13 13:25:10.301 -0600'"
DATE_INIT = "2025-05-05 13:25:10.301000-06:00"
DATE_END = "2025-05-05 13:25:10.301 -0600"


NUM_WORKERS = 4
CHUNK_SIZE = 1_000_000


# os.makedirs(DUMP_DIR, exist_ok=True)


def monitor_time(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        elapsed_time = end_time - start_time
        log(f"Execution time: {elapsed_time:.2f} seconds in {func.__name__}")
        return result

    return wrapper


def log(msg):
    # with open(LOG_FILE, "a") as f:
    #     f.write(f"{datetime.datetime.now()} - {msg}\n")
    print(msg)


@monitor_time
def get_data(offset: int, limit: int, conn):
    csv_buffer = io.StringIO()
    offset = offset + 1
    query = f"COPY (SELECT * FROM {SCHEMA_ORIGIN}.{TABLE_NAME} {QUERY} ORDER BY 1 OFFSET {offset} LIMIT {limit}) TO STDOUT WITH (FORMAT csv, DELIMITER '\t')"
    with conn.cursor() as cur:
        cur.copy_expert(
            query,
            csv_buffer,
        )
    # print(query)

    csv_buffer.seek(0)
    return csv_buffer


@monitor_time
def get_data_by_times(date_start: str, date_end: str, conn):
    csv_buffer = io.StringIO()
    query = f"COPY (SELECT * FROM {SCHEMA_ORIGIN}.{TABLE_NAME} where executed_at > '{date_start}' and executed_at < '{date_end}') TO STDOUT WITH (FORMAT csv, DELIMITER '\t')"
    with conn.cursor() as cur:
        cur.copy_expert(
            query,
            csv_buffer,
        )
    # print(query)

    csv_buffer.seek(0)
    return csv_buffer


@monitor_time
def insert_data(csv_buffer, conn):
    cur = conn.cursor()

    try:
        cur.copy_expert(
            f"COPY {SCHEMA_DEST}.{TABLE_NAME} FROM STDIN WITH (FORMAT csv, DELIMITER '\t')",
            csv_buffer,
        )
        conn.commit()
    except psycopg2.errors.UniqueViolation as e:
        log(f"Unique constraint violation: {e}")
        conn.rollback()
    except Exception as e:
        log(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()


@monitor_time
def count_rows(conn):
    with conn.cursor() as cur:
        if True:
            cur.execute(
                f"SELECT reltuples::bigint AS estimate FROM pg_class WHERE relname = %s",
                (TABLE_NAME,),
            )
        else:
            cur.execute(
                f"SELECT count(*) FROM {SCHEMA_ORIGIN}.{TABLE_NAME} {QUERY}",
            )
        estimate = cur.fetchone()[0]
    return estimate


def main():
    log(" >>>>>>>>>>>>  Starting migration <<<<<<<<<<<< ")
    conn_origin = psycopg2.connect(**FULL_CONN_ORIGIN)
    conn_dest = psycopg2.connect(**FULL_CONN_DEST)

    # ********* Get data by times *********
    data_start = datetime.strptime(DATE_INIT, "%Y-%m-%d %H:%M:%S.%f %z")
    data_end = datetime.strptime(DATE_END, "%Y-%m-%d %H:%M:%S.%f %z")
    delta = timedelta(days=1)

    while data_start < data_end:
        log(f"Insertando registros desde {data_start} hasta {data_start + delta}")
        csv_buffer = get_data_by_times(
            data_start.strftime("%Y-%m-%d %H:%M:%S.%f %z"),
            (data_start + delta).strftime("%Y-%m-%d %H:%M:%S.%f %z"),
            conn_origin,
        )
        insert_data(csv_buffer, conn_dest)
        data_start += delta

    # ********* Get data by offset *********

    # total_filas = count_rows(conn_origin) - 6_000_000
    # log(f"Total de registros a migrar: {total_filas:,}")

    # offsets = range(0, total_filas, CHUNK_SIZE)

    # for offset in offsets:
    #     log(f"Insertando registros desde {offset:,} hasta {(offset + CHUNK_SIZE):,}")
    #     csv_buffer = get_data(offset, CHUNK_SIZE, conn_origin)
    #     insert_data(csv_buffer, conn_dest)

    conn_origin.close()
    conn_dest.close()
    log(" >>>>>>>>>>>>  Migration completed <<<<<<<<<<<< ")


if __name__ == "__main__":
    main()
