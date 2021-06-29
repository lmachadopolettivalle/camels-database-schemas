from database_helpers import set_database_filename, execute_query

import pandas as pd

DATABASE_FILENAME = "sample.db"
set_database_filename(DATABASE_FILENAME)

def get_all_simulation_details():
    query = f"""
    SELECT 
    *
    FROM simulations
    """

    data = execute_query(query)
    return pd.DataFrame(data)


def get_halos_based_on_filters(list_of_inequality_filters, list_of_equality_filters):
    query = """
    SELECT
    *
    FROM halos
    """

    query_where_clauses = []

    for (column_name, lower_limit, upper_limit) in list_of_inequality_filters:
        if lower_limit is not None:
            query_where_clauses.append(f"{column_name} >= {lower_limit}")
        if upper_limit is not None:
            query_where_clauses.append(f"{column_name} <= {upper_limit}")

    for (column_name, values) in list_of_equality_filters:
        if isinstance(values[0], str):
            values = [f"'{v}'" for v in values]
        
        query_where_clauses.append(f"{column_name} IN ({','.join(values)})")

    if len(query_where_clauses) != 0:
        query += " WHERE " + " AND ".join(query_where_clauses)

    data = execute_query(query)
    return pd.DataFrame(data)



def get_profiles(list_of_halo_ids, list_of_simulation_ids, list_of_snapshots, list_of_properties):
    query = """
    SELECT
    *
    FROM profiles
    """

    query_where_clauses = []

    if len(list_of_halo_ids) != 0:
        halo_in_clause = "ID IN (" + ",".join([f"'{h}'" for h in list_of_halo_ids]) + ")"
        query_where_clauses.append(halo_in_clause)
    if len(list_of_simulation_ids) != 0:
        simulation_in_clause = "simulation_unique_id IN (" + ",".join([f"'{s}'" for s in list_of_simulation_ids]) + ")"
        query_where_clauses.append(simulation_in_clause)
    if len(list_of_snapshots) != 0:
        snapshot_in_clause = "snapshot IN (" + ",".join([f"'{s}'" for s in list_of_snapshots]) + ")"
        query_where_clauses.append(snapshot_in_clause)
    if len(list_of_properties) != 0:
        properties_in_clause = "property_key IN (" + ",".join([f"'{p}'" for p in list_of_properties]) + ")"
        query_where_clauses.append(properties_in_clause)

    if len(query_where_clauses) != 0:
        query += " WHERE " + " AND ".join(query_where_clauses)

    data = execute_query(query)
    return pd.DataFrame(data)


def get_subhalos(list_of_subhalo_ids, list_of_halo_ids, list_of_simulation_ids, list_of_snapshots, list_of_inequality_filters, list_of_equality_filters):
    query = """
    SELECT
    *
    FROM subhalos
    """

    query_where_clauses = []

    if len(list_of_subhalo_ids) != 0:
        subhalo_in_clause = "subhaloID IN (" + ",".join([f"'{h}'" for h in list_of_subhalo_ids]) + ")"
        query_where_clauses.append(subhalo_in_clause)
    if len(list_of_halo_ids) != 0:
        halo_in_clause = "haloID IN (" + ",".join([f"'{h}'" for h in list_of_halo_ids]) + ")"
        query_where_clauses.append(halo_in_clause)
    if len(list_of_simulation_ids) != 0:
        simulation_in_clause = "simulation_unique_id IN (" + ",".join([f"'{s}'" for s in list_of_simulation_ids]) + ")"
        query_where_clauses.append(simulation_in_clause)
    if len(list_of_snapshots) != 0:
        snapshot_in_clause = "snapshot IN (" + ",".join([f"'{s}'" for s in list_of_snapshots]) + ")"
        query_where_clauses.append(snapshot_in_clause)
    
    for (column_name, lower_limit, upper_limit) in list_of_inequality_filters:
        if lower_limit is not None:
            query_where_clauses.append(f"{column_name} >= {lower_limit}")
        if upper_limit is not None:
            query_where_clauses.append(f"{column_name} <= {upper_limit}")

    for (column_name, values) in list_of_equality_filters:
        if isinstance(values[0], str):
            values = [f"'{v}'" for v in values]
        
        query_where_clauses.append(f"{column_name} IN ({','.join(values)})")

    if len(query_where_clauses) != 0:
        query += " WHERE " + " AND ".join(query_where_clauses)

    data = execute_query(query)
    return pd.DataFrame(data)

def get_mergertree(starting_subfind_id, starting_snapshot, simulation_unique_id):
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
    
    profiles = get_profiles(
        list_of_halo_ids=[0, 1],
        list_of_simulation_ids=["IllustrisTNG_1P_22", "sample ID 2"],
        list_of_snapshots=[33],
        list_of_properties=["gas_density"]
    )
    print(profiles)

    subhalos = get_subhalos(
        list_of_subhalo_ids=[290],
        list_of_halo_ids=[0, 1],
        list_of_simulation_ids=["IllustrisTNG_1P_22"],
        list_of_snapshots=[33],
        list_of_inequality_filters=[],
        list_of_equality_filters=[]
    )
    print(subhalos)

    mergertree = get_mergertree(
        starting_subfind_id=0,
        starting_snapshot=33,
        simulation_unique_id="IllustrisTNG_LH_0"
    )
    print(mergertree)
