import argparse
import pandas as pd

from database_helpers import set_database_filename, create_table, populate_table
from illstack_helpers import get_illstack_global_properties, get_illstack_profile_properties

# Accept optional name of database file
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--database_filename", help="Database filename to be generated", default="sample.db", type=str)

args = parser.parse_args()
db_filename = args.database_filename

# Set database filename
set_database_filename(db_filename)

# Read simulation data from CAMELS text files
# Text files from https://github.com/franciscovillaescusa/CAMELS/tree/6bfc303f73f8778791afead51fbd4d399dff5516/setup/
CAMELS_simulations_textfiles = {
    "IllustrisTNG" : "CAMELS_parameters/CosmoAstroSeed_IllustrisTNG.txt",
    "SIMBA" : "CAMELS_parameters/CosmoAstroSeed_SIMBA.txt"
}

CAMELS_simulations_data = []

for simulation_suite, filename in CAMELS_simulations_textfiles.items():
    data = pd.read_csv(filename, delim_whitespace=True)

    for i, row in data.iterrows():
        CAMELS_entry = [
            f"{simulation_suite}_{row['#Name']}", # simulation_unique_id, e.g. IllustrisTNG_1P_22
            simulation_suite,
            row["#Name"], # simulation_name
            row["Omega_m"],
            row["sigma_8"],
            row["A_SN1"],
            row["A_AGN1"],
            row["A_SN2"],
            row["A_AGN2"],
            row["seed"],
        ]
        CAMELS_simulations_data.append(CAMELS_entry)


# Populate tables with computed data
### simulations
populate_table(
    "simulations",
    [
        "simulation_unique_id", "simulation_suite", "simulation_name", "Omega_m", "sigma_8", "A_SN1", "A_AGN1", "A_SN2", "A_AGN2", "seed"
    ],
    CAMELS_simulations_data
)
