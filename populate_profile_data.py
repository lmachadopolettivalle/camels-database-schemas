import argparse

from database_helpers import set_database_filename, create_table, populate_table
from illstack_helpers import get_illstack_global_properties, get_illstack_profile_properties

# Accept optional name of database file
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--database_filename", help="Database filename to be generated", default="sample.db", type=str)
parser.add_argument("--profile_filename", help="Profiles .npz file, used to determine columns for the profiles table", default="sample_illstack.npz", type=str)
parser.add_argument("--simulation_id", help="Unique ID for the simulation used in this datafile", default="IllustrisTNG_1P_22_z0.0", type=str)
parser.add_argument("--simulation_description", help="Helpful description of this simulation and its defining features", default="", type=str)
parser.add_argument("--simulation_redshift", help="Redshift for this simulation run", default=0, type=float)

args = parser.parse_args()
db_filename = args.database_filename
profile_filename = args.profile_filename
SIMULATION_ID = args.simulation_id
SIMULATION_DESCRIPTION = args.simulation_description
SIMULATION_REDSHIFT = args.simulation_redshift

# Set database filename
set_database_filename(db_filename)

# Get profile and halo data
radial_bins, illstack_profile_properties = get_illstack_profile_properties(profile_filename)
illstack_global_properties = get_illstack_global_properties(profile_filename)

# Populate tables with computed data
### simulations
populate_table(
    "simulations",
    [
        "simulation_unique_id", "simulation_description", "redshift"
    ],
    [
        (SIMULATION_ID, SIMULATION_DESCRIPTION, SIMULATION_REDSHIFT)
    ]
)


### halos
halo_unique_ids = [] # list of strings
halos_data = [] # List of tuples with halo properties
number_halos = len(illstack_global_properties[
    list(illstack_global_properties.keys())[0]
])

# Setup list of columns
halos_columns_list = ["halo_unique_id", "simulation_id"]
halos_columns_list.extend(list(illstack_global_properties.keys()))
print(halos_columns_list)

# Setup list of rows to be inserted
for i in range(number_halos):
    halos_entry = []
    halo_id = f"halo_{i}"
    halo_unique_ids.append(halo_id)
    halos_entry.append(halo_id) # halo_unique_id
    halos_entry.append(SIMULATION_ID) # simulation_id

    for v in illstack_global_properties.values():
        halos_entry.append(v[i])

    halos_data.append(tuple(halos_entry))

populate_table(
    "halos",
    halos_columns_list,
    halos_data
)


### profiles
profiles_data = [] # List of tuples with profile properties
number_halos = len(illstack_profile_properties[
    list(illstack_profile_properties.keys())[0]
])

for i in range(number_halos):
    for j, radius in enumerate(radial_bins):
        for k, v in illstack_profile_properties.items():
            profiles_entry = []
            profiles_entry.append(halo_unique_ids[i]) # halo_unique_id
            profiles_entry.append(SIMULATION_ID) # simulation_id
            profiles_entry.append(radius) # simulation_id

            profiles_entry.append(k) # property_key
            profiles_entry.append(v[i][j]) # property_value

            profiles_data.append(tuple(profiles_entry))

populate_table(
    "profiles",
    [
        "halo_unique_id", "simulation_id", "radius", "property_key", "property_value"
    ],
    profiles_data
)
