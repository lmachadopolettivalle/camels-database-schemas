import matplotlib.pyplot as plt
from filter_data_helpers import get_halos_based_on_filters, get_profiles

HUBBLE = 0.6711

# Select halos based on mass cut and simulation ID
halo_ids_result = get_halos_based_on_filters(
    list_of_inequality_filters=[("M_Crit200", 100/HUBBLE, 1e3/HUBBLE)],
    list_of_equality_filters=[("simulation_id", ["sample simulation ID"])]
)
print(halo_ids_result)


# Select profiles for the filtered halo IDs
halo_IDs = halo_ids_result["halo_unique_id"]
simulation_IDs = halo_ids_result["simulation_id"]

print(halo_IDs)
print(simulation_IDs)

profiles_result = get_profiles(
    list_of_halo_ids=halo_IDs,
    list_of_simulation_ids=simulation_IDs,
    list_of_properties=["gas_density"]
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


# Compute percentiles of profile data
profiles_16 = profiles_result.quantile(q=0.16, axis="columns")
profiles_84 = profiles_result.quantile(q=0.84, axis="columns")
profiles_median = profiles_result.quantile(q=0.5, axis="columns")


profiles_16.plot(logx=True)
profiles_84.plot(logx=True)
profiles_median.plot(logx=True)

plt.show()
