import argparse

from database_helpers import set_database_filename, create_table, remove_existing_db_files
from illstack_helpers import get_illstack_global_properties

# Accept optional name of database file
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--database_filename", help="Database filename to be generated", default="sample.db", type=str)
parser.add_argument("--profile_filename", help="Profiles .npz file, used to determine columns for the profiles table", default="sample_illstack.npz", type=str)
args = parser.parse_args()
db_filename = args.database_filename
profile_filename = args.profile_filename

# Set filename to be used in database creation
set_database_filename(db_filename)

# Remove database file if already exists
remove_existing_db_files()

# Step 1: create necessary tables
### simulations
create_table(
    "simulations",
    {
        "simulation_unique_id" : "TEXT PRIMARY KEY",
        "simulation_description" : "TEXT NOT NULL",
        "redshift" : "REAL NOT NULL",
        "feedback_efficiency" : "REAL NOT NULL",
        "omega_m" : "REAL NOT NULL",
        "omega_b" : "REAL NOT NULL",
        "box_size" : "REAL NOT NULL",
        "resolution" : "REAL NOT NULL",
    },
)


### halos
# based on list of properties from Illstack
halos_columns = {
    "halo_unique_id" : "TEXT NOT NULL",
    "simulation_id" : "TEXT NOT NULL",
}

illstack_global_properties = get_illstack_global_properties(profile_filename)

for k in illstack_global_properties.keys():
    halos_columns[k] = "REAL"

create_table(
    "halos",
    halos_columns
)

### profiles
create_table(
    "profiles",
    {
        "halo_unique_id" : "TEXT NOT NULL",
        "simulation_id" : "TEXT NOT NULL",
        "radius" : "REAL NOT NULL",
        "property_key" : "TEXT NOT NULL",
        "property_value" : "REAL"
    },
)

