import matplotlib.pyplot as plt
import numpy as np
from filter_data_helpers import get_halos_based_on_filters, get_profiles

HUBBLE = 0.6711

# Select halos based on mass cut and simulation ID
halo_ids_result = get_halos_based_on_filters(
    list_of_inequality_filters=[("M_Crit200", 1/HUBBLE, 1e5/HUBBLE)],
    list_of_equality_filters=[("simulation_unique_id", ["IllustrisTNG_1P_22"])]
)
print(halo_ids_result)


# Select profiles for the filtered halo IDs
halo_IDs = halo_ids_result["halo_unique_id"]
simulation_IDs = halo_ids_result["simulation_unique_id"]

print(halo_IDs)
print(simulation_IDs)

profiles_result = get_profiles(
    list_of_halo_ids=halo_IDs,
    list_of_simulation_ids=simulation_IDs,
    list_of_properties=["gas_density"] # See options in illstack_helpers.py
)

print(profiles_result)

# Rescale data to common units
profiles_result["radius"] *= 1 / (HUBBLE * 1e3) # Convert to Mpc
profiles_result["property_value"] *= 1e10 * HUBBLE * HUBBLE # Convert to Msun * kpc^-3

# Plot profiles for different halos
profiles_result = profiles_result.pivot(index="radius", columns="halo_unique_id", values="property_value")
print(profiles_result)

# Filter radial values
profiles_result = profiles_result[(profiles_result.index > 0.01) & (profiles_result.index < 3)]


# Bin halo_IDs by M_Crit200
mass_ranges = [(1, 2), (2, 10), (10, 100), (100, 1000)]
label_mass_ranges = [(1e10*low/HUBBLE, 1e10*high/HUBBLE) for (low, high) in mass_ranges]
halo_IDs_bins = [list(halo_ids_result[(halo_ids_result["M_Crit200"] >= low) & (halo_ids_result["M_Crit200"] < high)]["halo_unique_id"]) for (low, high) in mass_ranges]
print(halo_IDs_bins)

# Compute and plot percentiles of profile data
fig, ax = plt.subplots(1, 1, figsize=(8, 5))


for mass_range, halo_IDs_bin in zip(label_mass_ranges, halo_IDs_bins):
    low, high = np.log10(mass_range)

    binned_profiles = profiles_result[halo_IDs_bin]
    print(binned_profiles)

    profiles_16 = binned_profiles.quantile(q=0.16, axis="columns")
    profiles_84 = binned_profiles.quantile(q=0.84, axis="columns")
    profiles_median = binned_profiles.quantile(q=0.5, axis="columns")
    print(profiles_16)

    ax.fill_between(profiles_16.index, profiles_16, profiles_84, alpha=0.2)
    profiles_median.plot(label=f"{low:.1f} <=" + r" $log_{10} (M_{200c} / M_{\odot}) <$" + f" {high:.1f}")

# Display plot
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$r$ (Mpc)")
ax.set_ylabel(r"$\rho_{gas}$ ($M_{\odot} \cdot kpc^{-3}$)")

plt.legend()
plt.show()
