import numpy as np

# List of properties
global_properties_list = ['ID', 'M_Crit200', 'R_Crit200', 'GroupFirstSub', 'sfr', 'mstar', 'GroupBHMass', 'GroupBHMdot', 'Group_GasH', 'Group_GasHe', 'Group_GasC', 'Group_GasN', 'Group_GasO', 'Group_GasNe', 'Group_GasMg', 'Group_GasSi', 'Group_GasFe', 'GroupGasMetallicity', 'GroupLen', 'GroupMass', 'GroupNsubs', 'Group_StarH', 'Group_StarHe', 'Group_StarC', 'Group_StarN', 'Group_StarO', 'Group_StarNe', 'Group_StarMg', 'Group_StarSi', 'Group_StarFe', 'GroupStarMetallicity', 'GroupVelx', 'GroupVely', 'GroupVelz', 'GroupWindMass', 'M_Crit500', 'M_Mean200', 'M_TopHat200', 'R_Crit500', 'R_Mean200', 'R_TopHat200']

profile_properties_key = "val"
profile_properties_list = ["gas_density", "gas_pressure", "metallicity", "temperature"] # data["val"] is a 3D array (profile_type, value, radial bin). This is the list of profile types

def get_illstack_global_properties(profile_filename):
    with np.load(profile_filename, allow_pickle=True) as f:
        data = dict(f)

    global_properties_dict = {
        k : data[k]
        for k in global_properties_list
        if k in data.keys()
    }

    return global_properties_dict


def get_illstack_profile_properties(profile_filename):
    with np.load(profile_filename, allow_pickle=True) as f:
        data = dict(f)

    radial_bins = data["r"] # List of length 25 (25 == data["nbins"])

    profile_properties_dict = {
        profile_type : data[profile_properties_key][i,:]
        for i, profile_type in enumerate(profile_properties_list)
    }

    print(profile_properties_dict)

    return radial_bins, profile_properties_dict
