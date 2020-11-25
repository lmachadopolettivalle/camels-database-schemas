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

def execute_query(query: str):
    conn = get_db_conn()
    cursor = conn.cursor()

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


####################
# Sample usage of the database functions

# Step 1: create necessary tables
create_table(
    "halos",
    {
        "halo_id" : "INTEGER",
        "redshift" : "REAL NOT NULL",
        "property_id" : "INTEGER NOT NULL",
        "property_value" : "REAL"
    },
    primary_key = ("halo_id", "redshift", "property_id")
)

create_table(
    "halos_meta",
    {
        "property_id" : "INTEGER PRIMARY KEY",
        "property_description" : "TEXT NOT NULL",
        "units" : "TEXT NOT NULL"
    }
)

create_table(
    "profiles",
    {
        "halo_id" : "INTEGER",
        "redshift" : "REAL NOT NULL",
        "profile_property_id" : "INTEGER NOT NULL",
        "radius" : "INTEGER",
        "property_value" : "REAL"
    },
    primary_key=("halo_id", "redshift", "profile_property_id", "radius"),
    foreign_key={"local_column": "halo_id", "foreign_table": "halos", "foreign_column": "halo_id"}
)

create_table(
    "profiles_meta",
    {
        "profile_property_id" : "INTEGER PRIMARY KEY",
        "profile_property_description" : "TEXT NOT NULL",
        "units" : "TEXT NOT NULL"
    }
)

# Step 2: populate tables with computed data
populate_table(
    "halos",
    [
        "halo_id", "redshift", "property_id", "property_value"
    ],
    [
        (1234, 0.0, 1, 1e14),
        (1234, 0.0, 2, 1e15),
        (5678, 0.0, 1, 2e13),
        (129304937, 0.0, 1, 1e12),
    ]
)

populate_table(
    "halos_meta",
    [
        "property_id", "property_description", "units"
    ],
    [
        (1, "M500c", "Msun"),
        (2, "M200c", "Msun"),
    ]
)

populate_table(
    "profiles",
    [
        "halo_id", "redshift", "profile_property_id", "radius", "property_value"
    ],
    [
        (1234, 0.0, 1999, 100, 1e13),
        (1234, 0.0, 1999, 200, 2e13),
        (1234, 0.0, 1999, 300, 2.5e13),
        (1234, 0.0, 1999, 400, 3e13),
        (1234, 0.0, 1999, 500, 4e13),
        (5678, 0.0, 1999, 150, 1e12),
        (5678, 0.0, 1999, 200, 2e12),
        (5678, 0.0, 1999, 300, 3e12),
        (5678, 0.0, 1999, 450, 3.5e12),
        (5678, 2.0, 1999, 120, 1e12),
        (5678, 2.0, 2333, 150, 1e7),
        (5678, 2.0, 2333, 250, 5e6),
        (5678, 2.0, 2333, 300, 2e6),
        (5678, 2.0, 2333, 450, 8e5),
    ]
)

populate_table(
    "profiles_meta",
    [
        "profile_property_id", "profile_property_description", "units"
    ],
    [
        (1999, "DM Differential Density", "Msun Mpc^-3"),
        (2333, "Gas Temperature", "keV"),
    ]
)

# Step 3: select data from tables
## Determine halo_ids based on mass cut
halo_cut_property = "M500c"

halo_ids_query = f"""
SELECT h.halo_id, h.property_id, h.redshift, h.property_value, hm.property_description
FROM halos h
INNER JOIN halos_meta hm
ON h.property_id = hm.property_id
WHERE hm.property_description = '{halo_cut_property}'
AND h.property_value > 2e12
AND h.redshift = 0.0
"""

halo_ids = execute_query(halo_ids_query)
halo_ids_string_list = ','.join(str(halo_id["halo_id"]) for halo_id in halo_ids)

## Obtain specific profile data for these halo_ids
property_name = "DM Differential Density"

dm_profiles_query = f"""
SELECT p.halo_id, p.radius, p.property_value
FROM profiles p
INNER JOIN profiles_meta pm
ON p.profile_property_id = pm.profile_property_id
WHERE pm.profile_property_description = '{property_name}'
AND p.halo_id IN ({halo_ids_string_list})
AND redshift = 0.0
"""

profiles = execute_query(dm_profiles_query)

# Step 4: plot profiles
x = defaultdict(list)
y = defaultdict(list)
for row in profiles:
    x[row["halo_id"]].append(row["radius"])
    y[row["halo_id"]].append(row["property_value"])


for halo_id in x.keys():
    plt.scatter(
        x[halo_id],
        y[halo_id],
        label=f"{halo_id}"
    )
    plt.xlabel("Radius")
    plt.ylabel(property_name)

plt.legend()
plt.show()
