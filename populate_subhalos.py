# populate_subhalos should be executed in an environment with the following files available:
# offsets and postprocessing folders
import argparse
import numpy as np
import sys
sys.path.append("/home/jovyan")
import illustris_python as il

from database_helpers import set_database_filename, populate_table

# Accept optional name of database file
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--database_filename", help="Database filename to be generated", default="sample.db", type=str)
parser.add_argument("--snapshot", help="Snapshot number", type=str)
parser.add_argument("--halo_id", help="ID of the parent FoF Halo from which to load the subhalos", type=str)
parser.add_argument("--simulation_suite", help="Simulation suite in question (e.g. IllustrisTNG, SIMBA)", type=str)
parser.add_argument("--simulation_name", help="Simulation name in question (e.g. LH_0, 1P_22)", type=str)
parser.add_argument("--basepath", help="Absolute basepath to the CAMELS output files, used by illustris_python (e.g. '/home/jovyan/Simulations/')", type=str)

args = parser.parse_args()

db_filename = args.database_filename
snapshot = int(args.snapshot)
halo_id = int(args.halo_id)
simulation_suite = args.simulation_suite # e.g. IllustrisTNG
simulation_name = args.simulation_name # e.g. LH_0
basepath = f"{args.basepath}/{args.simulation_suite}/{args.simulation_name}/" # e.g. /home/jovyan/Simulations/IllustrisTNG/LH_0/

simulation_unique_id = f"{simulation_suite}_{simulation_name}"

# Set database filename
set_database_filename(db_filename)

# Use illustris_python to load subhalos in the given snapshot and simulation
subhalo_fields = ["SubhaloBHMass", "SubhaloBHMdot", "SubhaloBfldDisk", "SubhaloBfldHalo", "SubhaloCM", "SubhaloGasMetalFractions", "SubhaloGasMetalFractionsHalfRad", "SubhaloGasMetalFractionsMaxRad", "SubhaloGasMetalFractionsSfr", "SubhaloGasMetalFractionsSfrWeighted", "SubhaloGasMetallicity", "SubhaloGasMetallicityHalfRad", "SubhaloGasMetallicityMaxRad", "SubhaloGasMetallicitySfr", "SubhaloGasMetallicitySfrWeighted", "SubhaloGrNr", "SubhaloHalfmassRad", "SubhaloHalfmassRadType", "SubhaloIDMostbound", "SubhaloLen", "SubhaloLenType", "SubhaloMass", "SubhaloMassInHalfRad", "SubhaloMassInHalfRadType", "SubhaloMassInMaxRad", "SubhaloMassInMaxRadType", "SubhaloMassInRad", "SubhaloMassInRadType", "SubhaloMassType", "SubhaloParent", "SubhaloPos", "SubhaloSFR", "SubhaloSFRinHalfRad", "SubhaloSFRinMaxRad", "SubhaloSFRinRad", "SubhaloSpin", "SubhaloStarMetalFractions", "SubhaloStarMetalFractionsHalfRad", "SubhaloStarMetalFractionsMaxRad", "SubhaloStarMetallicity", "SubhaloStarMetallicityHalfRad", "SubhaloStarMetallicityMaxRad", "SubhaloStellarPhotometrics", "SubhaloStellarPhotometricsMassInRad", "SubhaloStellarPhotometricsRad", "SubhaloVel", "SubhaloVelDisp", "SubhaloVmax", "SubhaloVmaxRad", "SubhaloWindMass"]
subhalos = il.groupcat.loadSubhalos(basepath, snapshot, fields=subhalo_fields)
subhalo_fields.remove("SubhaloGrNr") # Do not include it as part of the insert query below, since it's already included as "haloID"

# Filter subhalos based on FoF halo ID (i.e. "SubhaloGrNr")
mask = np.where((subhalos["SubhaloGrNr"] == halo_id))[0]

# Set up dataset for database
subhalos_data= list(
    zip(
        list(mask), # subhaloID
        list(subhalos["SubhaloGrNr"][mask]), # haloID
        [simulation_unique_id] * len(mask), # simulation_unique_id
        [snapshot] * len(mask), # Snapshot Number
        *[list(subhalos[field][mask]) for field in subhalo_fields],
    )
)

print(subhalos["SubhaloBHMass"][mask])
print(type(subhalos["SubhaloBHMass"][mask][0]))

# Setup list of columns
subhalos_columns_list = ["subhaloID", "haloID", "simulation_unique_id", "snapshot"]
subhalos_columns_list.extend(subhalo_fields)

populate_table(
    "subhalos",
    subhalos_columns_list,
    subhalos_data
)
