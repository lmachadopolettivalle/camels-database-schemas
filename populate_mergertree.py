# populate_mergertree should be executed in an environment with the following files available:
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
parser.add_argument("--subhalo_id", help="ID of the subhalo for which we should load the Sublink mergertree", type=str)
parser.add_argument("--simulation_suite", help="Simulation suite in question (e.g. IllustrisTNG, SIMBA)", type=str)
parser.add_argument("--simulation_name", help="Simulation name in question (e.g. LH_0, 1P_22)", type=str)
parser.add_argument("--basepath", help="Absolute basepath to the CAMELS output files, used by illustris_python (e.g. '/home/jovyan/Simulations/')", type=str)

args = parser.parse_args()

db_filename = args.database_filename
snapshot = int(args.snapshot)
subhalo_id = int(args.subhalo_id)
simulation_suite = args.simulation_suite # e.g. IllustrisTNG
simulation_name = args.simulation_name # e.g. LH_0
basepath = f"{args.basepath}/{args.simulation_suite}/{args.simulation_name}/" # e.g. /home/jovyan/Simulations/IllustrisTNG/LH_0/

simulation_unique_id = f"{simulation_suite}_{simulation_name}"

# Set database filename
set_database_filename(db_filename)

# Use illustris_python to load subhalos in the given snapshot and simulation
mergertree_additional_fields = ["LastProgenitorID", "MainLeafProgenitorID", "RootDescendantID", "TreeID", "FirstProgenitorID", "NextProgenitorID", "DescendantID", "FirstSubhaloInFOFGroupID", "NextSubhaloInFOFGroupID", "NumParticles", "Mass", "MassHistory"]
mergertree_fields = ["SubhaloID", "SubfindID", "SnapNum"] + mergertree_additional_fields
mergertree = il.sublink.loadTree(basepath, snapshot, subhalo_id, fields=mergertree_fields, onlyMPB=False)

if mergertree is None:
    # Subhalo is not in tree
    exit()

# Set up dataset for database
mergertree_data = list(
    zip(
        [simulation_unique_id] * mergertree["count"],
        list(mergertree["SnapNum"]),
        list(mergertree["SubhaloID"]),
        list(mergertree["SubfindID"]),
        *[list(mergertree[field]) for field in mergertree_additional_fields],
    )
)

# Setup list of columns
mergertree_columns = ["simulation_unique_id", "snapshot", "subhaloID", "subfindID"]
mergertree_columns.extend(mergertree_additional_fields)

populate_table(
    "mergertree",
    mergertree_columns,
    mergertree_data
)
