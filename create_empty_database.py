import argparse
import numpy as np

from database_helpers import set_database_filename, create_table, remove_existing_db_files
from illstack_helpers import get_illstack_global_properties

# Accept optional name of database file
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--database_filename", help="Database filename to be generated", default="sample.db", type=str)
parser.add_argument("--profile_filename", help="Profiles .npz file, used to determine columns for the profiles table", required=True, type=str)
args = parser.parse_args()
db_filename = args.database_filename
profile_filename = args.profile_filename

# Set filename to be used in database creation
set_database_filename(db_filename)

# Remove database file if already exists
remove_existing_db_files()

# Create necessary tables
### simulations
# Table schema motivated by https://camels.readthedocs.io/en/latest/IllustrisTNG_params.html#illustristng-params
create_table(
    "simulations",
    {
        "simulation_unique_id" : "TEXT PRIMARY KEY", # IllustrisTNG_1P_22
        "simulation_suite" : "TEXT NOT NULL", # IllustrisTNG, SIMBA
        "simulation_name" : "TEXT NOT NULL", # LH_0, 1P_22
        "Omega_m" : "REAL NOT NULL",
        "sigma_8" : "REAL NOT NULL",
        "A_SN1" : "REAL NOT NULL",
        "A_AGN1" : "REAL NOT NULL",
        "A_SN2" : "REAL NOT NULL",
        "A_AGN2" : "REAL NOT NULL",
        "seed" : "REAL NOT NULL",
    },
    unique=("simulation_suite", "simulation_name")
)


### halos
# based on list of properties from Illstack
halos_columns = {
    "snapshot" : "INTEGER NOT NULL",
    "simulation_unique_id" : "TEXT NOT NULL",
}

illstack_global_properties = get_illstack_global_properties(profile_filename)

for k in illstack_global_properties.keys():
    element = illstack_global_properties[k][0]
    if isinstance(element, np.uint32) or isinstance(element, np.int16) or isinstance(element, np.int32) or isinstance(element, np.int64) or isinstance(element, int):
        halos_columns[k] = "INTEGER"
    else:
        halos_columns[k] = "REAL"

create_table(
    "halos",
    halos_columns,
    unique=("snapshot", "simulation_unique_id", "ID")
)

### profiles
create_table(
    "profiles",
    {
        "ID" : "INTEGER NOT NULL",
        "simulation_unique_id" : "TEXT NOT NULL",
        "snapshot" : "INTEGER NOT NULL",
        "radius" : "REAL NOT NULL",
        "property_key" : "TEXT NOT NULL",
        "property_value" : "REAL",
    },
    unique=("ID", "simulation_unique_id", "snapshot", "radius", "property_key")
)

### subhalos
# Properties motivated by https://www.tng-project.org/data/docs/specifications/#sec2b
create_table(
    "subhalos",
    {
        "subhaloID" : "INTEGER NOT NULL",
        "haloID" : "INTEGER NOT NULL",
        "simulation_unique_id" : "TEXT NOT NULL",
        "snapshot" : "INTEGER NOT NULL",
        "SubhaloBHMass" : "REAL",
        "SubhaloBHMdot" : "REAL",
        "SubhaloBfldDisk" : "REAL",
        "SubhaloBfldHalo" : "REAL",
        "SubhaloCM" : "ARRAY",
        "SubhaloGasMetalFractions" : "ARRAY",
        "SubhaloGasMetalFractionsHalfRad" : "ARRAY",
        "SubhaloGasMetalFractionsMaxRad" : "ARRAY",
        "SubhaloGasMetalFractionsSfr" : "ARRAY",
        "SubhaloGasMetalFractionsSfrWeighted" : "ARRAY",
        "SubhaloGasMetallicity" : "REAL",
        "SubhaloGasMetallicityHalfRad" : "REAL",
        "SubhaloGasMetallicityMaxRad" : "REAL",
        "SubhaloGasMetallicitySfr" : "REAL",
        "SubhaloGasMetallicitySfrWeighted" : "REAL",
        "SubhaloHalfmassRad" : "REAL",
        "SubhaloHalfmassRadType" : "ARRAY",
        "SubhaloIDMostbound" : "REAL",
        "SubhaloLen" : "REAL",
        "SubhaloLenType" : "ARRAY",
        "SubhaloMass" : "REAL",
        "SubhaloMassInHalfRad" : "REAL",
        "SubhaloMassInHalfRadType" : "ARRAY",
        "SubhaloMassInMaxRad" : "REAL",
        "SubhaloMassInMaxRadType" : "ARRAY",
        "SubhaloMassInRad" : "REAL",
        "SubhaloMassInRadType" : "ARRAY",
        "SubhaloMassType" : "ARRAY",
        "SubhaloParent" : "REAL",
        "SubhaloPos" : "ARRAY",
        "SubhaloSFR" : "REAL",
        "SubhaloSFRinHalfRad" : "REAL",
        "SubhaloSFRinMaxRad" : "REAL",
        "SubhaloSFRinRad" : "REAL",
        "SubhaloSpin" : "ARRAY",
        "SubhaloStarMetalFractions" : "ARRAY",
        "SubhaloStarMetalFractionsHalfRad" : "ARRAY",
        "SubhaloStarMetalFractionsMaxRad" : "ARRAY",
        "SubhaloStarMetallicity" : "REAL",
        "SubhaloStarMetallicityHalfRad" : "REAL",
        "SubhaloStarMetallicityMaxRad" : "REAL",
        "SubhaloStellarPhotometrics" : "ARRAY",
        "SubhaloStellarPhotometricsMassInRad" : "REAL",
        "SubhaloStellarPhotometricsRad" : "REAL",
        "SubhaloVel" : "ARRAY",
        "SubhaloVelDisp" : "REAL",
        "SubhaloVmax" : "REAL",
        "SubhaloVmaxRad" : "REAL",
        "SubhaloWindMass" : "REAL",
    },
    unique=("subhaloID", "haloID", "simulation_unique_id", "snapshot")
)

### mergertree
# Properties motivated by https://www.tng-project.org/data/docs/specifications/#sec4a
create_table(
    "mergertree",
    {
        "subhaloID" : "INTEGER NOT NULL", # In mergertree, subhaloID is a unique ID, and has NOTHING to do with subhaloID from the subhalos table. To match with the subhaloID from the subhalos table, look at the "subfindID" column within this table.
        "subfindID" : "INTEGER NOT NULL", # This corresponds to "subhaloID" in the subhalos table. The combination (subfindID, snapshot) is a unique identifier of any subhalo within a simulation.
        "snapshot" : "INTEGER NOT NULL",
        "simulation_unique_id" : "TEXT NOT NULL",
        "LastProgenitorID" : "INTEGER NOT NULL",
        "MainLeafProgenitorID" : "INTEGER NOT NULL",
        "RootDescendantID" : "INTEGER NOT NULL",
        "TreeID" : "INTEGER NOT NULL",
        "FirstProgenitorID" : "INTEGER NOT NULL",
        "NextProgenitorID" : "INTEGER NOT NULL",
        "DescendantID" : "INTEGER NOT NULL",
        "FirstSubhaloInFOFGroupID" : "INTEGER NOT NULL",
        "NextSubhaloInFOFGroupID" : "INTEGER NOT NULL",
        "NumParticles" : "INTEGER NOT NULL",
        "Mass" : "REAL NOT NULL",
        "MassHistory" : "INTEGER NOT NULL",
    },
    unique=("subhaloID", "subfindID", "snapshot", "simulation_unique_id")
)
