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

exit()
quit()

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
