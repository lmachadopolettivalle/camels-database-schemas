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
ID, M_Crit200
FROM halos
WHERE
M_Crit200 <= {high_mass_cut}
AND
M_Crit200 > {low_mass_cut}
LIMIT 2000
"""

data = execute_query(query)
#print(data)

halo_ids = [row["ID"] for row in data]


property_key = "gas_pressure"

query = f"""
SELECT 
ID, radius, property_value
FROM profiles
WHERE
property_key = ?
AND
ID IN ({','.join(['?' for _ in halo_ids])})
ORDER BY ID, radius
"""

params = (property_key, *halo_ids)

data = execute_query(query, params)
#print(data)

profiles = defaultdict(dict)
for row in data:
    halo_id = row["ID"]
    if "radius" not in profiles[halo_id]:
        profiles[halo_id]["radius"] = []
        profiles[halo_id]["property"] = []

    profiles[halo_id]["radius"].append(row["radius"] / (HUBBLE * 1000)) # Dividing by 1000 to convert into Mpc

    #profiles[halo_id]["property"].append(row["property_value"] * 1e10 * HUBBLE * HUBBLE / ((3.086*1e12)**2)) # Turn from CAMELS units to CGS
    #profiles[halo_id]["property"].append(row["property_value"]) # 1e10 Msol/h*(km/s)^2 /(ckpc/h)^3
    #profiles[halo_id]["property"].append(row["property_value"] * 1e10 * HUBBLE * HUBBLE) # Msol*(km/s)^2 /(kpc)^3
    profiles[halo_id]["property"].append(row["property_value"] * 1e10 * HUBBLE * HUBBLE * (3.2*1e-17)**2) # Msol * kpc^-1 * s^-2

#print(profiles)

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

plt.xlim(0.01, 5) # Mimic sample Jupyter notebook from Emily
plt.xscale("log")
plt.yscale("log")

plt.xlabel(r"R [Mpc]")
plt.ylabel(r"$P$ [Msol * kpc^-1 * s^-2]")




# Sanity checks from arxiv 2009.05558 (ACT)
G = 4.3 * 1e-3 # pc * Msun^-1 * km^2 * s^-2
G *= 1e-6 * (1000/(3.08*1e22))**2 # Convert to Mpc^3 * Msun^-1 * s^-2


x_ck = 0.6
P_0 = 2
alpha_t = 0.8
beta_t = 2.6
gamma_t = -0.3
A_t2 = 0.7

f_baryons = 0.049 / 0.309
rho_crit_at_redshift = 1.878*1e-26 * HUBBLE * HUBBLE # kg m^-3
rho_crit_at_redshift *= (1/(1.989*1e30)) * (1/(3.08*1e22))**(-3) # Convert to Msun * Mpc^-3

def pressure_GNFW(r):
    R_200 = 0.1 # Mpc
    M_200 = 100 * 1e10 / HUBBLE # Msun
    P_200 = 200 * G * M_200 * rho_crit_at_redshift * f_baryons / (2 * R_200) # Msun * Mpc^-1 * s^-2
    P_200 *= 1e-3 # Convert to Msun * kpc^-1 * s^-2

    x = r / R_200

    P = P_0 * ((x / x_ck) ** gamma_t) * (1+(x/x_ck)**alpha_t) ** (-beta_t)
    P *= P_200

    return P


radii = [0.01, 0.03, 0.1, 0.3, 1, 3]
gnfw = [pressure_GNFW(i) for i in radii]
plt.plot(radii, gnfw, lw=3, label="ACT GNFW fit (Amodeo+2020)")

plt.legend()

plt.show()
