import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here

    # Create a DataFrame with unique toll IDs
    toll_ids = pd.concat([df['id_1'], df['id_2']]).unique()
    toll_matrix = pd.DataFrame(index=toll_ids, columns=toll_ids)

    # Initialize the matrix with infinity values
    toll_matrix[:] = float('inf')

    # Fill in known distances
    for _, row in df.iterrows():
        toll_matrix.at[row['id_1'], row['id_2']] = row['distance']
        toll_matrix.at[row['id_2'], row['id_1']] = row['distance']  # Ensure matrix is symmetric

    # Apply Floyd-Warshall algorithm to compute shortest paths
    for k in toll_ids:
        for i in toll_ids:
            for j in toll_ids:
                toll_matrix.at[i, j] = min(toll_matrix.at[i, j], toll_matrix.at[i, k] + toll_matrix.at[k, j])

    # Set diagonal values to 0
    for i in toll_ids:
        toll_matrix.at[i, i] = 0

    return toll_matrix


def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here
    # Create an empty DataFrame to store unrolled distances
    unrolled_df = pd.DataFrame(columns=['id_start', 'id_end', 'distance'])

    # Iterate through each combination of id_start and id_end
    for id_start in df.index:
        for id_end in df.columns:
            # Skip combinations where id_start is equal to id_end
            if id_start != id_end:
                distance = df.at[id_start, id_end]
                unrolled_df = unrolled_df.append({'id_start': id_start, 'id_end': id_end, 'distance': distance}, ignore_index=True)

    return unrolled_df



def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Calculate average distance for the reference ID
    reference_avg_distance = df[df['id_start'] == reference_id]['distance'].mean()

    # Calculate the lower and upper bounds for the threshold
    lower_bound = reference_avg_distance * 0.9
    upper_bound = reference_avg_distance * 1.1

    # Filter the DataFrame based on the threshold
    filtered_df = df[(df['id_start'] != reference_id) & (df['distance'] >= lower_bound) & (df['distance'] <= upper_bound)]

    # Sort the DataFrame by id_start
    sorted_df = filtered_df.sort_values(by='id_start')

    return sorted_df


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    # Define rate coefficients for each vehicle type
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Add columns for each vehicle type with toll rates
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate_coefficient

    return df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Define time intervals and discount factors
    time_intervals = [
        (datetime.strptime('00:00:00', '%H:%M:%S').time(), datetime.strptime('10:00:00', '%H:%M:%S').time(), 0.8),
        (datetime.strptime('10:00:00', '%H:%M:%S').time(), datetime.strptime('18:00:00', '%H:%M:%S').time(), 1.2),
        (datetime.strptime('18:00:00', '%H:%M:%S').time(), datetime.strptime('23:59:59', '%H:%M:%S').time(), 0.8)
    ]

    weekend_discount_factor = 0.7

    # Add columns for start_day, start_time, end_day, and end_time
    df['start_day'] = df['startDay'].replace({1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'})
    df['end_day'] = df['endDay'].replace({1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'})
    df['start_time'] = pd.to_datetime(df['startTime'], format='%H:%M:%S').dt.time
    df['end_time'] = pd.to_datetime(df['endTime'], format='%H:%M:%S').dt.time

    # Apply time-based discount factors
    for start_time, end_time, discount_factor in time_intervals:
        mask = (df['start_time'] >= start_time) & (df['end_time'] <= end_time)
        for vehicle_type in ['moto', 'car', 'rv', 'bus', 'truck']:
            df.loc[mask, vehicle_type] *= discount_factor

    # Apply constant discount factor for weekends
    weekend_mask = df['startDay'].isin(['Saturday', 'Sunday'])
    for vehicle_type in ['moto', 'car', 'rv', 'bus', 'truck']:
        df.loc[weekend_mask, vehicle_type] *= weekend_discount_factor

    return df