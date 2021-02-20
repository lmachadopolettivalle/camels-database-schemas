from database_helpers import set_database_filename, execute_query

import pandas as pd

DATABASE_FILENAME = "sample.db"
set_database_filename(DATABASE_FILENAME)

def get_all_simulation_details():
    query = f"""
    SELECT 
    simulation_unique_id, simulation_description, redshift
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



def get_profiles(list_of_halo_ids, list_of_simulation_ids, list_of_properties):
    query = """
    SELECT
    *
    FROM profiles
    """

    query_where_clauses = []

    if len(list_of_halo_ids) != 0:
        halo_in_clause = "halo_unique_id IN (" + ",".join([f"'{h}'" for h in list_of_halo_ids]) + ")"
        query_where_clauses.append(halo_in_clause)
    if len(list_of_simulation_ids) != 0:
        simulation_in_clause = "simulation_id IN (" + ",".join([f"'{s}'" for s in list_of_simulation_ids]) + ")"
        query_where_clauses.append(simulation_in_clause)
    if len(list_of_properties) != 0:
        properties_in_clause = "property_key IN (" + ",".join([f"'{p}'" for p in list_of_properties]) + ")"
        query_where_clauses.append(properties_in_clause)

    if len(query_where_clauses) != 0:
        query += " WHERE " + " AND ".join(query_where_clauses)

    data = execute_query(query)
    return pd.DataFrame(data)


if __name__ == "__main__":
    get_all_simulation_details()
    get_halos_based_on_filters(
        list_of_inequality_filters=[("M_Crit200", 30, 200)],
        list_of_equality_filters=[("simulation_id", ["testsimu", "banana"])],
    )

    get_profiles(
        list_of_halo_ids=["halo_0", "nonexistent halo ID"],
        list_of_simulation_ids=["simulation ID 1", "testsimu"],
        list_of_properties=["gas_density"]
    )
