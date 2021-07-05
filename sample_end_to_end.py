import matplotlib.pyplot as plt
import numpy as np
from filter_data_helpers import get_halos_based_on_filters, get_profiles_for_halos

HUBBLE = 0.6711

# Select halos based on mass cut and simulation ID
halo_ids_result = get_halos_based_on_filters(
    list_of_inequality_filters=[("M_Crit200", 1/HUBBLE, 1e5/HUBBLE)],
    list_of_equality_filters=[("simulation_unique_id", ["IllustrisTNG_1P_22", "IllustrisTNG_LH_1"])]
)
print(halo_ids_result)


# Select profiles for the filtered halo IDs
profiles_result = get_profiles_for_halos(
    list_of_halos=halo_ids_result[["ID", "simulation_unique_id", "snapshot"]],
    list_of_properties=["gas_density"] # See options in illstack_helpers.py, or enter [] to receive all available profiles
)

print(profiles_result)

# Rescale data to common units
profiles_result["radius"] *= 1 / (HUBBLE * 1e3) # Convert to Mpc
profiles_result["property_value"] *= 1e10 * HUBBLE * HUBBLE # Convert to Msun * kpc^-3

# Plot profiles for different halos

# Filter radial values
profiles_result = profiles_result[(profiles_result["radius"] > 0.01) & (profiles_result["radius"] < 3)]
print(profiles_result)

# Bin halo_IDs by M_Crit200
mass_ranges = [(1, 2), (2, 10), (10, 100), (100, 1000)]
halo_IDs_bins = [list(halo_ids_result[(halo_ids_result["M_Crit200"] >= low) & (halo_ids_result["M_Crit200"] < high)]["ID"]) for (low, high) in mass_ranges]
print(halo_IDs_bins)

# Convert units
label_mass_ranges = [(1e10*low/HUBBLE, 1e10*high/HUBBLE) for (low, high) in mass_ranges]

# Obtain all unique (simulation, snapshot) combinations in profiles dataset
sim_snap_combinations = profiles_result.index.drop_duplicates().to_numpy()

# Compute and plot percentiles of profile data
fig, ax = plt.subplots(1, 1, figsize=(8, 5))

for mass_range in label_mass_ranges:
    low, high = np.log10(mass_range)

    halos_filtered = halo_ids_result[(halo_ids_result["M_Crit200"] >= low) & (halo_ids_result["M_Crit200"] < high)]

    for sim, snapshot in sim_snap_combinations:
        # Determine halo IDs within this simulation and snapshot
        sim_snap_halo_ids = halos_filtered[(halos_filtered["simulation_unique_id"] == sim) & (halos_filtered["snapshot"] == snapshot)]["ID"]
        # Determine profiles for this simulation and snapshot (use .loc since (simulation, snapshot) is the MultiIndex for the profiles DataFrame)
        sim_snap_profiles = profiles_result.loc[(sim, snapshot)]
        # Filter profiles based on halo IDs
        sim_snap_profiles = sim_snap_profiles[sim_snap_profiles["ID"].isin(sim_snap_halo_ids)]
        # Only keep radius and property_value columns
        sim_snap_profiles = sim_snap_profiles[["radius", "property_value"]]

        # Determine median and percentiles for the profile data, and plot
        median_profiles = sim_snap_profiles.groupby("radius", as_index=False).median()

        ax.plot(
            median_profiles["radius"],
            median_profiles["property_value"],
            label=f"{sim} / {snapshot}, Mass within ({low:.1f} {high:.1f})"
        )

        # Display quantiles
        profiles_16 = sim_snap_profiles.groupby("radius", as_index=False).quantile(q=0.16)
        profiles_84 = sim_snap_profiles.groupby("radius", as_index=False).quantile(q=0.84)
        ax.fill_between(profiles_16["radius"], profiles_16["property_value"], profiles_84["property_value"], alpha=0.2)

# Display plot
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$r$ (Mpc)")
ax.set_ylabel(r"$\rho_{gas}$ ($M_{\odot} \cdot kpc^{-3}$)")

plt.legend()
plt.show()
