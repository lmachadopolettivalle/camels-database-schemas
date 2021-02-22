import matplotlib.pyplot as plt
from filter_data_helpers import get_halos_based_on_filters, get_profiles

# Select halos based on mass cut and simulation ID
halo_ids_result = get_halos_based_on_filters(
    list_of_inequality_filters=[("M_Crit200", 100, 1e3)],
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

# Plot profiles for different halos
profiles_result = profiles_result.pivot(index="radius", columns="halo_unique_id", values="property_value")
print(profiles_result)

profiles_result.plot(logx=True)

plt.show()
