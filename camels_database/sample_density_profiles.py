import populate_profile_data # Executes generation of database
from database_helpers import execute_query

from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
#print(data)

halo_ids = [row["halo_unique_id"] for row in data]


property_key = "gas_density"

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
#print(data)

profiles = defaultdict(dict)
for row in data:
    halo_id = row["halo_unique_id"]
    if "radius" not in profiles[halo_id]:
        profiles[halo_id]["radius"] = []
        profiles[halo_id]["property"] = []

    profiles[halo_id]["radius"].append(row["radius"] / (HUBBLE * 1000)) # Dividing by 1000 to convert into Mpc

    profiles[halo_id]["property"].append(row["property_value"] * 1e10 * HUBBLE * HUBBLE)

print(profiles)

# Make DataFrame with profile data
profiles_df = pd.DataFrame.from_dict(profiles, orient="index")
print(profiles_df)

# Make mean, 16 %, 84 %

radii = np.percentile(
    list(profiles_df["radius"]),
    q=50,
    axis=0
)
median = np.percentile(
    list(profiles_df["property"]),
    q=50,
    axis=0
)

per_16 = np.percentile(
    list(profiles_df["property"]),
    q=16,
    axis=0
)
per_84 = np.percentile(
    list(profiles_df["property"]),
    q=84,
    axis=0
)

print(median)

#for halo_id, d in profiles.items():
#    plt.plot(d["radius"], d["property"],label=halo_id, alpha=0.2)
plt.plot(radii, median, label="CAMELS")
plt.fill_between(radii, per_16, per_84, alpha=0.2)

plt.xlim(0.01, 3) # Mimic sample Jupyter notebook from Emily
plt.xscale("log")
plt.yscale("log")

plt.xlabel(r"R [Mpc]")
plt.ylabel(r"$\rho$ [Msun * kpc^-3]")


# Sanity checks from arxiv 2009.05558 (ACT)
rho_0 = 10**2.8
x_ck = 0.6
beta_k = 2.6
A_k2 = 1.1

alpha_k = 1
gamma_k = -0.2

f_baryons = 0.049 / 0.309
rho_crit_at_redshift = 1.878*1e-26 * HUBBLE * HUBBLE # kg m^-3
rho_crit_at_redshift *= (1/(1.989*1e30)) * (1/(3.08*1e19))**(-3) # Convert to Msun * kpc^-3

def rho_GNFW(r):
    R_200 = 0.1 # Mpc
    x = r / R_200
    rho = rho_0 * ((x / x_ck) ** gamma_k) * ((1+(x/x_ck)**alpha_k) ** ((gamma_k - beta_k)/alpha_k))
    rho *= f_baryons * rho_crit_at_redshift

    return rho

radii = [0.01, 0.03, 0.1, 0.3, 1, 3]
gnfw = [rho_GNFW(i) for i in radii]
plt.plot(radii, gnfw, label="ACT GNFW fit (Amodeo+2020)")

plt.legend()

plt.show()
