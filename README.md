# camels-database-schemas

Prototype for SQL database to store CAMELS-CGM working group data.

Motivated by previous work from https://github.com/ethlau/caps/tree/main

## Settings

### Data Sources
- Halos and Profiles: Emily Moser with Illstack (https://github.com/emilymmoser/illstack_CAMELS)
- Mergers and Mergertree: Viraj Pandya with Rockstar

### Data Sizes and Memory Requirements
TBD

### Tables and Schemas
- halos
- profiles
- simulations

### Helpful SQL browser extension
The following browser extension helps debug the `sqlite` database file: https://add0n.com/sqlite-manager.html

## Usage

### Setup
```
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

### One-Time Scripts to populate database
To create a new empty database file:
```
python create_empty_database.py -f "sample.db" --profile_filename "IllustrisTNG_1P_22_0.0.npz"
```

To populate the simulation metadata:
```
python populate_simulations_table.py -f "sample.db"
```

To populate the profile data (using only one file):
```
python populate_profile_data.py -f "sample.db" --profile_filename "IllustrisTNG_1P_22_0.0.npz"
```

OR, to populate the profile data (using all available files):
(NOTE: this assumes all `.npz` files are in the root directory, where the scripts are executed)
```
python bulk_populate_profiles.py
```

### Analysis Scripts to fetch data:

Useful SQL query/filtering functions:
```
python filter_data_helpers.py
```

Sample end to end script to query database and plot resulting radial profiles:
```
python sample_end_to_end.py
```
