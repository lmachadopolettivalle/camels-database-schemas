import argparse

from database_helpers import set_database_filename, create_table, populate_table
from illstack_helpers import get_illstack_global_properties, get_illstack_profile_properties

# Accept optional name of database file
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--database_filename", help="Database filename to be generated", default="sample.db", type=str)
parser.add_argument("--profile_filename", help="Profiles .npz file. Name: 'simulationsuite_simulationname_redshift_...', e.g. 'IllustrisTNG_1P_22_0.0_...'", required=True, type=str)

args = parser.parse_args()
db_filename = args.database_filename
profile_filename = args.profile_filename

# Determine simulation details from the filename
# Filenames: "simulationsuite_simulationname_redshift_...", e.g. "IllustrisTNG_1P_22_0.0_..."
# Important! This assumes that all simulation names contain an underscore. E.g. "1P_22"
simulation_details = profile_filename.split("_")

SIMULATION_SUITE = simulation_details[0]
SIMULATION_NAME = f"{simulation_details[1]}_{simulation_details[2]}" # Assumes all simulation names have an underscore in them
SIMULATION_REDSHIFT = float(simulation_details[3].replace(".npz", ""))
#print(SIMULATION_REDSHIFT)
SIMULATION_UNIQUE_ID = f"{SIMULATION_SUITE}_{SIMULATION_NAME}"

# Set database filename
set_database_filename(db_filename)

# Get profile and halo data
radial_bins, illstack_profile_properties = get_illstack_profile_properties(profile_filename)
illstack_global_properties = get_illstack_global_properties(profile_filename)

# Populate tables with computed data
### halos
halo_ids = illstack_global_properties["ID"] # list of halo IDs
halos_data = [] # List of tuples with halo properties
number_halos = len(illstack_global_properties[
    list(illstack_global_properties.keys())[0]
])

# Setup list of columns
halos_columns_list = ["simulation_unique_id", "redshift"]
halos_columns_list.extend(list(illstack_global_properties.keys()))

# Setup list of rows to be inserted
for i in range(number_halos):
    halos_entry = []
    halos_entry.append(SIMULATION_UNIQUE_ID) # simulation_unique_id
    halos_entry.append(SIMULATION_REDSHIFT) # redshift

    for k, v in illstack_global_properties.items():
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
            profiles_entry.append(halo_ids[i]) # halo_unique_id
            profiles_entry.append(SIMULATION_UNIQUE_ID) # simulation_unique_id
            profiles_entry.append(SIMULATION_REDSHIFT) # redshift
            profiles_entry.append(radius) # radius

            profiles_entry.append(k) # property_key
            profiles_entry.append(v[i][j]) # property_value

            profiles_data.append(tuple(profiles_entry))

populate_table(
    "profiles",
    [
        "ID", "simulation_unique_id", "redshift", "radius", "property_key", "property_value"
    ],
    profiles_data
)
