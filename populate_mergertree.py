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
snapshot_string = f"{args.snapshot:0>3}" # Snapshot, padded to 3 digits (e.g. 001)
snapshot_int = int(args.snapshot)
subhalo_id = int(args.subhalo_id)
simulation_suite = args.simulation_suite # e.g. IllustrisTNG
simulation_name = args.simulation_name # e.g. LH_0
basepath = f"{args.basepath}/{args.simulation_suite}/{args.simulation_name}/" # e.g. /home/jovyan/Simulations/IllustrisTNG/LH_0/

simulation_unique_id = f"{simulation_suite}_{simulation_name}"

# Determine redshift from snapshot
SNAPSHOT_TO_REDSHIFT = {'000':6.0,'001':5.0,'002':4.0,'003':3.5,'004':3.0,'005':2.81329,'006':2.63529,'007':2.46560,'008':2.30383,'009':2.14961,'010':2.00259,'011':1.86243,'012':1.72882,'013':1.60144,'014':1.48001,'015':1.36424,'016':1.25388,'017':1.14868,'018':1.04838,'019':0.95276,'020':0.86161,'021':0.77471,'022':0.69187,'023':0.61290,'024':0.53761,'025':0.46584,'026':0.39741,'027':0.33218,'028':0.27,'029':0.21072,'030':0.15420,'031':0.10033,'032':0.04896,'033':0.0}
redshift = SNAPSHOT_TO_REDSHIFT[snapshot_string]

# Set database filename
set_database_filename(db_filename)

# Use illustris_python to load subhalos in the given snapshot and simulation
mergertree_additional_fields = ["LastProgenitorID"]
mergertree_fields = ["SubhaloID", "SubfindID", "SnapNum"] + mergertree_additional_fields
mergertree = il.sublink.loadTree(basepath, snapshot_int, fields=mergertree_fields, onlyMPB=False)








# Set up dataset for database
mergertree_data = list(
    zip(
        [simulation_unique_id] * mergertree["count"],
        [SNAPSHOT_TO_REDSHIFT[i] for i in mergertree["SnapNum"]],
        list(mergertree["SubhaloID"]),
        list(mergertree["SubfindID"]),
        list(mergertree["LastProgenitorID"]),
    )
)

# Setup list of columns
mergertree_columns = ["simulation_unique_id", "redshit", "subhaloID", "subfindID"]
mergertree_columns.extend(mergertree_additional_fields)

populate_table(
    "mergertree",
    mergertree_columns,
    mergertree_data
)
