from database_helpers import create_table, remove_existing_db_files
from illstack_helpers import get_illstack_global_properties

remove_existing_db_files()

# Step 1: create necessary tables
### simulations
create_table(
    "simulations",
    {
        "simulation_unique_id" : "TEXT PRIMARY KEY",
        "simulation_description" : "TEXT NOT NULL",
        "redshift" : "REAL NOT NULL",
    },
)


### halos
# based on list of properties from Illstack
halos_columns = {
    "halo_unique_id" : "TEXT NOT NULL",
    "simulation_id" : "TEXT NOT NULL",
}

illstack_global_properties = get_illstack_global_properties()

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

