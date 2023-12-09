import pandas as pd



def generate_car_matrix(df)->pd.DataFrame:
    """
    Creates a DataFrame  for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values, 
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    # Write your logic here

    # Pivot the dataframe to get car values with id_1 as index and id_2 as columns
    car_matrix = df.pivot(index='id_1', columns='id_2', values='car')
    
    # Fill NaN values with 0
    car_matrix = car_matrix.fillna(0)
    
    # Set diagonal values to 0
    for index in car_matrix.index:
        car_matrix.at[index, index] = 0
    
    return car_matrix


def get_type_count(df)->dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Write your logic here

    # settting all value to low for car type column
    df['car_type'] = 'low'
    
    # setting all values to medium for car values greater than 15
    df.loc[df['car'] > 15, 'car_type'] = 'medium'


    # setting all values to high for car values greater than 25
    df.loc[df['car'] > 25, 'car_type'] = 'high'

    # Calculate the count of occurrences for each car_type category
    type_counts = df['car_type'].value_counts().to_dict()

    # Sort the dictionary alphabetically based on keys
    sorted_type_counts = {k: type_counts[k] for k in sorted(type_counts)}

    #returning dictinory
    return sorted_type_counts


def get_bus_indexes(df)->list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Write your logic here
    # Calculate the mean of the 'bus' column
    bus_mean = df['bus'].mean()

    # Find the indexes where 'bus' values exceed twice the mean
    bus_indexes = df[df['bus'] > 2 * bus_mean].index.tolist()

    return bus_indexes


def filter_routes(df)->list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Write your logic here
    # Group by 'route' and calculate the mean of 'truck' values for each group
    route_means = df.groupby('route')['truck'].mean()

    # Filter routes where the average 'truck' value is greater than 7
    filtered_routes = route_means[route_means > 7].index.tolist()

    return filtered_routes


def multiply_matrix(matrix)->pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Write your logic here
    # Apply custom conditions to modify values
    modified_matrix = matrix.applymap(lambda x: x * 0.75 if x > 20 else x * 1.25)

    # Round the values to 1 decimal place
    modified_matrix = modified_matrix.round(1)

    return modified_matrix


def time_check(df)->pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: return a boolean series
    """
    # Write your logic here
    # Combine startDay and startTime to create a datetime column for the start timestamp
    df['start_timestamp'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'])
    
    # Combine endDay and endTime to create a datetime column for the end timestamp
    df['end_timestamp'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'])

    # Check if each unique (id, id_2) pair covers a full 24-hour period and spans all 7 days
    completeness_check = (
        df.groupby(['id', 'id_2'])
        .apply(lambda group: (
            group['start_timestamp'].min() == pd.Timestamp('00:00:00') and
            group['end_timestamp'].max() == pd.Timestamp('23:59:59') and
            group['start_timestamp'].dt.dayofweek.unique().size == 7
        ))
    )

    return completeness_check
