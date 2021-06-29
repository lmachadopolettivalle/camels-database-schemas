# The first step is to populate the "halos" table.
# Then, we load all subhalos belonging to the stored FoF halos,
# and populate the :subhalos" table accordingly.

from database_helpers import execute_query
import pandas as pd
import subprocess

BASEPATH = "/home/jovyan/Simulations/"

# Determine all unique (simulation, snapshot, halo_id) combinations from the "halos" table.
query = """
SELECT
DISTINCT snapshot, simulation_unique_id, ID
FROM halos
"""

data = execute_query(query)
halos = pd.DataFrame(data)
for _, halo in halos.iterrows():
    snapshot = halo["snapshot"]
    halo_id = halo['ID']
    simulation_unique_id = halo["simulation_unique_id"]
    simulation_details = simulation_unique_id.split("_")
    simulation_suite = simulation_details[0]
    simulation_name = f"{simulation_details[1]}_{simulation_details[2]}"

    command = f"""python3 populate_subhalos.py -f "sample.db" --snapshot {snapshot} --halo_id {halo_id} --simulation_suite {simulation_suite} --simulation_name {simulation_name} --basepath {BASEPATH}"""
    print(command)

    cmd = subprocess.run(command, shell=True)
    print(cmd)
