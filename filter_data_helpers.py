from typing import Union

from numpy import where
from database_helpers import set_database_filename, execute_query

import pandas as pd

DATABASE_FILENAME = "sample.db"
set_database_filename(DATABASE_FILENAME)

def get_all_simulation_details() -> pd.DataFrame:
    query = f"""
    SELECT 
    *
    FROM simulations
    """

    data = execute_query(query)
    return pd.DataFrame(data)


INEQUALITY_FILTER = tuple[str, float, float] # e.g. ("M_Crit200", 30, 200)
EQUALITY_FILTER = tuple[str, list] # e.g. ("simulation_unique_id", ["IllustrisTNG_1P_22", "SIMBA_LH_1"])
def _build_inequality_clause(
        list_of_inequality_filters: list[INEQUALITY_FILTER]
    ) -> list[str]:

    where_clauses_list = []

    for (column_name, lower_limit, upper_limit) in list_of_inequality_filters:
        if lower_limit is not None:
            where_clauses_list.append(f"{column_name} >= {lower_limit}")
        if upper_limit is not None:
            where_clauses_list.append(f"{column_name} <= {upper_limit}")

    return where_clauses_list

def _build_equality_clause(
        list_of_equality_filters: list[EQUALITY_FILTER]
    ) -> list[str]:

    where_clauses_list = []

    for (column_name, values) in list_of_equality_filters:
        if isinstance(values[0], str):
            values = [f"'{v}'" for v in values]
        else:
            values = [str(v) for v in values]
        
        where_clauses_list.append(f"{column_name} IN ({','.join(values)})")

    return where_clauses_list

def get_halos_based_on_filters(
        list_of_inequality_filters: list[INEQUALITY_FILTER],
        list_of_equality_filters: list[EQUALITY_FILTER]
    ) -> pd.DataFrame:
    """Given lists of equalities and inequalities,
    return the corresponding FoF halo entries.
    
    Keyword Arguments:
    list_of_inequality_filters: list of filters. Each filter contains a property name, a minimum and a maximum value.
    - e.g. for one filter: ("M_Crit200", 30, 200)
    list_of_equality_filters: list of filters. Each filter contains a property name and a list of accepted values.
    - e.g. for one filter: ("simulation_unique_id", ["IllustrisTNG_1P_22"])
    """

    query = """
    SELECT
    *
    FROM halos
    """

    query_where_clauses = []
    query_where_clauses.extend(_build_equality_clause(list_of_equality_filters))
    query_where_clauses.extend(_build_inequality_clause(list_of_inequality_filters))

    if len(query_where_clauses) != 0:
        query += " WHERE " + " AND ".join(query_where_clauses)

    data = execute_query(query)
    return pd.DataFrame(data)



def get_profiles_for_halos(
        list_of_halos: Union[pd.DataFrame, list[dict]],
        list_of_properties: list[str]
    ) -> pd.DataFrame:
    """Given a list of halos and a list of desired properties,
    return the corresponding radial profiles.
    
    Keyword Arguments:
    list_of_halos -- A dict, or pandas.DataFrame, containing the following keys:
    - ID: halo IDs, e.g. 0
    - simulation_unique_id: e.g. IllustrisTNG_1P_22
    - snapshot: e.g. 33
    list_of_properties -- list of strings, each of which match a property stored in the 'profiles' table.
    - e.g. ["gas_density", "metallicity"]
    """

    # If given a list, convert to pandas.DataFrame, for ease of iteration
    if isinstance(list_of_halos, list):
        list_of_halos = pd.DataFrame(list_of_halos)

    # SQL cannot handle a direct query with several (>1000) conditions.
    # As a result, we perform several queries,
    # one for each (simulation_unique_id, snapshot) combination,
    # and combine the results in the end before returning.
    simulation_snapshot_combinations = list_of_halos[["simulation_unique_id", "snapshot"]].drop_duplicates()

    list_of_results = []

    for _, row in simulation_snapshot_combinations.iterrows():
        # for each (sim, snap), do query to get profiles
        simulation_unique_id = row["simulation_unique_id"]
        snapshot = row["snapshot"]

        query = f"SELECT * FROM profiles WHERE simulation_unique_id = '{simulation_unique_id}' AND snapshot = {snapshot}"
        if len(list_of_properties) != 0:
            query += " AND property_key IN (" + ",".join([f"'{p}'" for p in list_of_properties]) + ")"

        IDs = list_of_halos[
            (list_of_halos["simulation_unique_id"] == simulation_unique_id) & (list_of_halos["snapshot"] == snapshot)
        ]["ID"]

        IDs = set(IDs)

        query += " AND ID IN (" + ", ".join([str(i) for i in IDs]) + ")"
        print(query)
        data = execute_query(query)
        result = pd.DataFrame(data)
        print(result)

        list_of_results.append(result)

    # Combine all results in one DataFrame
    profiles = pd.concat(list_of_results, ignore_index=True)
    print(profiles)
    # Use (simulation_unique_id, snapshot) as the index for the resulting DataFrame
    profiles = profiles.set_index(["simulation_unique_id", "snapshot"]).sort_index()
    # to get the index as tuples, use profiles.index.to_numpy()

    return profiles

def get_subhalos_based_on_filters(
        list_of_subhalos: Union[pd.DataFrame, list[dict]],
        list_of_inequality_filters: list[INEQUALITY_FILTER],
        list_of_equality_filters: list[EQUALITY_FILTER]
    ) -> pd.DataFrame:
    """Given a list of subhalos and/or lists of desired filters,
    return the corresponding subhalo entries.
    
    Keyword Arguments:
    list_of_subhalos -- A dict, or pandas.DataFrame, containing the following keys:
    - subhaloID: subhalo IDs, e.g. 0
    - simulation_unique_id: e.g. IllustrisTNG_1P_22
    - snapshot: e.g. 33
    list_of_inequality_filters: list of filters. Each filter contains a property name, a minimum and a maximum value.
    - e.g. for one filter: ("M_Crit200", 30, 200)
    list_of_equality_filters: list of filters. Each filter contains a property name and a list of accepted values.
    - e.g. for one filter: ("simulation_unique_id", ["IllustrisTNG_1P_22"])
    """

    # If given a list, convert to pandas.DataFrame, for ease of iteration
    if isinstance(list_of_subhalos, list):
        list_of_subhalos = pd.DataFrame(list_of_subhalos)

    query = """
    SELECT
    *
    FROM subhalos
    """

    subhalos_where_clauses = []

    for _, subhalo in list_of_subhalos.iterrows():
        where_clause = f"(subhaloID = {subhalo['subhaloID']} AND simulation_unique_id = '{subhalo['simulation_unique_id']}' AND snapshot = {subhalo['snapshot']})"
        subhalos_where_clauses.append(where_clause)

    filter_where_clauses = []
    filter_where_clauses.extend(_build_equality_clause(list_of_equality_filters))
    filter_where_clauses.extend(_build_inequality_clause(list_of_inequality_filters))

    where_clause = ""

    if len(subhalos_where_clauses) != 0:
        where_clause += "(" + " OR ".join(subhalos_where_clauses) + ")"
    
    if len(filter_where_clauses) != 0:
        if where_clause != "":
            where_clause += " AND "
        where_clause += " AND ".join(filter_where_clauses)
    
    if where_clause != "":
        query += " WHERE " + where_clause

    data = execute_query(query)
    return pd.DataFrame(data)

def get_mergertree(
        starting_subfind_id: int,
        starting_snapshot: int,
        simulation_unique_id: str
    ) -> pd.DataFrame:
    """Given a simulation, and a starting subhalo at a starting snapshot,
    return the complete mergertree from the given snapshot going backwards in time.

    Keyword Arguments:
    starting_subfind_id: Corresponds to the "subhaloID" column in the 'subhalos' table. The subhaloID of the first element of the mergertree.
    snapshot: The starting snapshot, at which the given subhaloID exists. The mergertree will search backwards in time from this snapshot.
    simulation_unique_id: e.g. "IllustrisTNG_1P_22". The simulation wherein to search for the mergertree.
    """

    # First, find the subhalo's "MainLeafProgenitorID", which marks the end of the tree
    query = f"""
    SELECT 
    subhaloID, MainLeafProgenitorID
    FROM mergertree
    WHERE subfindID = {starting_subfind_id}
    AND snapshot = {starting_snapshot}
    AND simulation_unique_id = "{simulation_unique_id}"
    """

    starting_data = execute_query(query)[0]
    main_leaf_progenitor_id = starting_data["MainLeafProgenitorID"]
    starting_subhalo_id = starting_data["subhaloID"]

    # Then, find the entire tree between the subfindID and the MainLeafProgenitorID
    query = f"""
    SELECT 
    *
    FROM mergertree
    WHERE subhaloID >= {starting_subhalo_id} and subhaloID <= {main_leaf_progenitor_id}
    AND simulation_unique_id = "{simulation_unique_id}"
    ORDER BY snapshot DESC
    """

    data = execute_query(query)
    return pd.DataFrame(data)

if __name__ == "__main__":
    simulations = get_all_simulation_details()
    print(simulations)

    halos = get_halos_based_on_filters(
        list_of_inequality_filters=[("M_Crit200", 30, 200)],
        list_of_equality_filters=[("simulation_unique_id", ["IllustrisTNG_1P_22", "sample ID 2"])],
    )
    print(halos)
    HUBBLE = 0.6711
    halos = get_halos_based_on_filters(
    list_of_inequality_filters=[("M_Crit200", 1/HUBBLE, 1e5/HUBBLE)],
    list_of_equality_filters=[("simulation_unique_id", ["IllustrisTNG_1P_22", "IllustrisTNG_LH_1"])]
    )

    list_of_halos = halos[["ID", "simulation_unique_id", "snapshot"]]

    profiles = get_profiles_for_halos(
        list_of_halos=list_of_halos,
        list_of_properties=["gas_density", "gas_pressure"]
    )
    print(profiles)

    subhalos = get_subhalos_based_on_filters(
        list_of_subhalos=[],
        list_of_inequality_filters=[("SubhaloBHMass", 0.01, 0.4)],
        list_of_equality_filters=[("haloID", [0, 1])]
    )
    print(subhalos)

    mergertree = get_mergertree(
        starting_subfind_id=0,
        starting_snapshot=33,
        simulation_unique_id="IllustrisTNG_LH_0"
    )
    print(mergertree)
