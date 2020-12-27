from collections import defaultdict
import io
from matplotlib import pyplot as plt
import numpy as np
import os
import sqlite3

DATABASE_FILE = "sample.db"
# For demo purposes, remove previous version of database
if os.path.isfile(DATABASE_FILE):
    os.remove("sample.db")


####################
# Helpers for storing numpy arrays

# From https://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("ARRAY", convert_array)


####################
# Database helper functions

def get_db_conn():
    conn = sqlite3.connect(DATABASE_FILE, detect_types=sqlite3.PARSE_DECLTYPES, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, params: tuple = None):
    conn = get_db_conn()
    cursor = conn.cursor()

    if params is not None:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    results = cursor.fetchall()

    # Only SELECT queries return non-empty lists
    if len(results) > 0:
        results = [dict(row) for row in results]

    conn.commit()
    cursor.close()
    conn.close()

    return results

def executemany_query(query: str, data: list):
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.executemany(query, data)

    conn.commit()
    cursor.close()
    conn.close()

def create_table(table_name: str, columns: dict, primary_key: tuple = None, foreign_key: dict = None):
    """ Create a table in the database
    table_name: Example = "halos"
    columns: Example = {
        "halo_id" : "INTEGER PRIMARY KEY",
        "halo_M500c" : "REAL"
    }
    """

    columns_list = [f"{k} {v}" for k, v in columns.items()]
    if primary_key is not None:
        columns_list.append(f"PRIMARY KEY ({', '.join(primary_key)})")
    if foreign_key is not None:
        columns_list.append(f"FOREIGN KEY ({foreign_key['local_column']}) REFERENCES {foreign_key['foreign_table']} ({foreign_key['foreign_column']})")

    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name}
    (
    {', '.join(columns_list)}
    )
    """

    execute_query(query)


def populate_table(table_name: str, columns: list, data: list):
    columns_string = ", ".join(columns)
    values_placeholders = ", ".join(["?" for _ in columns])

    query = f"""
    INSERT INTO {table_name}
    ({columns_string})
    VALUES ({values_placeholders})
    """

    executemany_query(query, data)

