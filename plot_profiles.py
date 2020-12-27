import populate_profile_data # Executes generation of database
from database_helpers import execute_query

from collections import defaultdict
import matplotlib.pyplot as plt

HUBBLE = 0.6711

low_mass_cut = 1.0
high_mass_cut = 1e5

low_mass_cut /= HUBBLE
high_mass_cut /= HUBBLE

query = f"""
SELECT 
halo_unique_id, M_Crit200
FROM halos
WHERE
M_Crit200 <= {high_mass_cut}
AND
M_Crit200 > {low_mass_cut}
LIMIT 2000
"""

data = execute_query(query)
print(data)

halo_ids = [row["halo_unique_id"] for row in data]


property_key = "val" # gas density

query = f"""
SELECT 
halo_unique_id, radius, property_value
FROM profiles
WHERE
property_key = ?
AND
halo_unique_id IN ({','.join(['?' for _ in halo_ids])})
ORDER BY halo_unique_id, radius
"""

params = (property_key, *halo_ids)

data = execute_query(query, params)
print(data)

profiles = defaultdict(dict)
for row in data:
    halo_id = row["halo_unique_id"]
    if "radius" not in profiles[halo_id]:
        profiles[halo_id]["radius"] = []
        profiles[halo_id]["property"] = []

    profiles[halo_id]["radius"].append(row["radius"] / (HUBBLE * 1000))
    profiles[halo_id]["property"].append(row["property_value"] * 1e10 * HUBBLE * HUBBLE)

print(profiles)


for halo_id, d in profiles.items():
    plt.plot(d["radius"], d["property"],label=halo_id, alpha=0.2)

plt.xlim(0.01, 5) # Mimic sample Jupyter notebook from Emily
plt.xscale("log")
plt.yscale("log")
#plt.legend()
plt.show()
