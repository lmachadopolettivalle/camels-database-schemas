# camels-database-schemas

Prototype for SQL database to store CAMELS-CGM working group data.

Motivated by previous work from https://github.com/ethlau/caps/tree/main

## Setup
```
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Scripts
To populate the SQL database:
```
python populate_profile_data.py
```

To fetch profile information and plot data:
```
python sample_plot_profiles.py
```

## Features

- Create tables using `sqlite` to store profile and halo information
- Select and plot profile data

## Helpful SQL browser extension

The following browser extension helps debug the `sqlite` database file: https://add0n.com/sqlite-manager.html

