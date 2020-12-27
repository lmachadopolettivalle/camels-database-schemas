from database_helpers import create_table, populate_table
from illstack_helpers import get_illstack_global_properties, get_illstack_profile_properties

SIMULATION_ID = "IllustrisTNG_1P_22_z0.0"
SIMULATION_DESCRIPTION = "IllustrisTNG, 1P_22"
SIMULATION_REDSHIFT = 0.0

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

radial_bins, illstack_profile_properties = get_illstack_profile_properties()
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

# Step 2: populate tables with computed data
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
    list(halos_columns.keys()),
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
