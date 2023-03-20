"""
    Air Transport System Analysis Project
    
    By:
        Abdallah Mohamed
        Muhammed Atef
        Youssef Fawzy
        
    Requirements:
        routes_manual.xlsx  --  File with routes data.
            
        Columns: 
            id
            airline_iata	
            origin_iata	
            deprt_time	
            dest_iata	
            duration	
            engine	
            ac_type	
            capacity	
            distance
            price_usd
            
"""

import pandas as pd
import numpy as np
import math
from datetime import date, timedelta, datetime as dt
import time


# Setup:
routes_filename = "routes.xlsx"
distances_filename = "distances.xlsx"
coefficients_filename = "coefficients.xlsx"
demands_filename = "demands.xlsx"

regional_jet_capacity = 110     # Defines what's a regional jet over a narrow-body airliner
dummy_date = "2023-01-01"       # Used to create datetime objects as the model is deisnged over 1 day

# Conditions:
max_first_layover = 240         # min
max_second_layover = 240        # min
min_layover = 30                # min
default_max_distance = 1200     # km
max_distance_factor = 1.7

# Functions
def get_city_pairs(cities):
    city_pairs = []
    for first_city in cities:
        for second_city in cities:
            if (first_city != second_city) and ([first_city, second_city] not in city_pairs):
                city_pairs.append([first_city, second_city])

    return city_pairs


def get_cities(df):
    cities = np.unique(
        np.append(df.dest_iata.unique(), df.origin_iata.unique())
        ).tolist()
    return cities


def get_airlines(df):
    airlines = df.airline_iata.unique().tolist()
    return airlines
    

def clean_data(df):
    clean_df = df
    df.rename(columns={'engine':'prop'}, inplace=True)
    df.replace({'prop': {'Prop': 1, 'Jet': 0}}, inplace=True)
    clean_df['regional'] = ((clean_df['prop'] == 0) & (clean_df['capacity'] <= regional_jet_capacity)).astype(int)
    clean_df['duration'] = pd.to_timedelta(clean_df['duration'])
    clean_df['deprt_time'] = clean_df['deprt_time'].astype('string')
    clean_df['deprt_time'] = dummy_date + " " + clean_df['deprt_time']    
    clean_df['deprt_time'] = pd.to_datetime(clean_df['deprt_time'])
    return clean_df

    
def get_city_pair_itineraries(routes_df, city_pair, airlines):
    
    # Main Loop:
    resultant_columns = list(routes_df.columns.values)
    resultant_columns.extend([
        'flight_path', 
        'city_pair',
        'arrive_time',
        'flight_legs',
        'service_lvl',
        'first_layover',
        'second_layover',
        'first_transfer_city',
        'second_transfer_city'
        ])
    resultant_itns = pd.DataFrame(columns=resultant_columns)
    
    city_pair_str = city_pair[0] + "_" + city_pair[1]
    
    # print(f"\n\n {city_pair} \n\n")
    
    for airline in airlines:
        
        # ------------ NON STOP ITINERARIES ------------
        
        airline_itns = routes_df[routes_df['airline_iata'] == airline]
        routes_with_origin = airline_itns[airline_itns['origin_iata'] == city_pair[0]]
        nonstop_itns = routes_with_origin[routes_with_origin['dest_iata'] == city_pair[1]]

        # Add non-stop itineraries to resultant df
        # Loop over each id in the nonstop_itns dataframe
        for this_id in nonstop_itns.id:
            # nonstop_itn is the row you're at, where its id equals the id the loop is at
            nonstop_itn = nonstop_itns[nonstop_itns['id'] == this_id].copy()
            nonstop_itn['flight_path'] = city_pair[0] + " -> " + city_pair[1]
            nonstop_itn['first_transfer_city'] = ""
            nonstop_itn['second_transfer_city'] = ""
            nonstop_itn['city_pair'] = city_pair_str
            nonstop_itn['arrive_time'] = nonstop_itn['deprt_time'].iloc[0] + nonstop_itn['duration'].iloc[0]
            nonstop_itn['flight_legs'] = [[nonstop_itn['id'].iloc[0]]]
            nonstop_itn['service_lvl'] = 0
            nonstop_itn['first_layover'] = timedelta(hours=0)
            nonstop_itn['second_layover'] = timedelta(hours=0)
            
            resultant_itns = pd.concat([resultant_itns, nonstop_itn])
                        
        # If a shortest non-stop itinerary is available, the max valid distance for 
        # itineraries is set based on it, where the max is its value times a factor 
        # if no non-stop itineraries present, a default value is used
        max_distance = default_max_distance if math.isnan(nonstop_itns.distance.min()) else (nonstop_itns.distance.min() * max_distance_factor)
        
        other_routes = routes_with_origin[~ routes_with_origin['id'].isin(nonstop_itns.id)]
        
        # Iterating over each route other than the non-stop itineraries
        for this_id in other_routes.id:
            first_leg = other_routes[other_routes['id'] == this_id]
            first_to_airport = first_leg.dest_iata.iloc[0]
            
            # ------------ ONE STOP ITINERARIES ------------
            
            # Extract all possible flight legs to be joined with first leg to make itinerary based on conditions
            possible_legs = airline_itns[
                (airline_itns['origin_iata'] == first_to_airport) 
                & (airline_itns['dest_iata'] == city_pair[1])
                & (airline_itns['deprt_time'] > (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0]))
                & ((airline_itns['deprt_time'] - (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0])) < timedelta(minutes = max_first_layover))
                & ((airline_itns['deprt_time'] - (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0])) > timedelta(minutes = min_layover))
                & (airline_itns['distance'] + first_leg['distance'].iloc[0] < max_distance)
            ]
            
            # Generate all one-stop itineraries
            for this_id_2 in possible_legs.id:
                second_leg = possible_legs[possible_legs['id'] == this_id_2]
                
                onestop_itn = first_leg.copy()
                onestop_itn['dest_iata'] = second_leg['dest_iata'].iloc[0]
                onestop_itn['arrive_time'] = second_leg['deprt_time'].iloc[0] + second_leg['duration'].iloc[0]
                onestop_itn['duration'] = onestop_itn['arrive_time'].iloc[0] - onestop_itn['deprt_time'].iloc[0]
                onestop_itn['regional'] = 1 if (first_leg['regional'].iloc[0] or second_leg['regional'].iloc[0]) else 0
                onestop_itn['prop'] = 1 if ((not onestop_itn['regional'].iloc[0]) and (first_leg['prop'].iloc[0] or second_leg['prop'].iloc[0])) else 0
                onestop_itn['capacity'] = min(first_leg['capacity'].iloc[0], second_leg['capacity'].iloc[0])
                onestop_itn['distance'] = first_leg['distance'].iloc[0] + second_leg['distance'].iloc[0]
                onestop_itn['flight_legs'] = [[first_leg['id'].iloc[0], second_leg['id'].iloc[0]]]
                onestop_itn['flight_path'] = city_pair[0] + " -> " + first_leg.dest_iata.iloc[0] + " -> " + city_pair[1]
                onestop_itn['first_transfer_city'] = first_leg.dest_iata.iloc[0]
                onestop_itn['second_transfer_city'] = ""
                onestop_itn['city_pair'] = city_pair_str
                onestop_itn['service_lvl'] = 1 if (first_leg['ac_type'].iloc[0] == second_leg['ac_type'].iloc[0]) else 2
                onestop_itn['first_layover'] = second_leg['deprt_time'].iloc[0] - (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0])
                onestop_itn['second_layover'] = timedelta(hours=0)
                
                resultant_itns = pd.concat([resultant_itns, onestop_itn])
            
            # ------------ TWO STOP ITINERARIES ------------
            
            possible_second_legs = airline_itns[
                (airline_itns['origin_iata'] == first_to_airport) 
                & (airline_itns['dest_iata'] != city_pair[1])
                & (airline_itns['dest_iata'] != first_leg['origin_iata'].iloc[0])
                & (airline_itns['deprt_time'] > (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0]))
                & ((airline_itns['deprt_time'] - (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0])) < timedelta(minutes = max_first_layover))
                & ((airline_itns['deprt_time'] - (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0])) > timedelta(minutes = min_layover))
                & (airline_itns['distance'] + first_leg['distance'].iloc[0] < max_distance)
            ]
            
            for this_id_2 in possible_second_legs.id:
                second_leg = possible_second_legs[possible_second_legs['id'] == this_id_2]
                second_to_airport = second_leg.dest_iata.iloc[0]
                
                possible_final_legs = airline_itns[
                    (airline_itns['origin_iata'] == second_to_airport) 
                    & (airline_itns['dest_iata'] == city_pair[1])
                    & (airline_itns['deprt_time'] > (second_leg['deprt_time'].iloc[0] + second_leg['duration'].iloc[0]))
                    & ((airline_itns['deprt_time'] - (second_leg['deprt_time'].iloc[0] + second_leg['duration'].iloc[0])) < timedelta(minutes = max_second_layover))
                    & ((airline_itns['deprt_time'] - (second_leg['deprt_time'].iloc[0] + second_leg['duration'].iloc[0])) > timedelta(minutes = min_layover))
                    & (airline_itns['distance'] + first_leg['distance'].iloc[0] + second_leg['distance'].iloc[0] < max_distance)
                ]
                
                for this_id_3 in possible_final_legs.id:
                    third_leg = possible_final_legs[possible_final_legs['id'] == this_id_3]
                    
                    twostop_itn = first_leg.copy()
                    twostop_itn['dest_iata'] = third_leg['dest_iata'].iloc[0]
                    twostop_itn['arrive_time'] = third_leg['deprt_time'].iloc[0] + third_leg['duration'].iloc[0]
                    twostop_itn['duration'] = twostop_itn['arrive_time'].iloc[0] - twostop_itn['deprt_time'].iloc[0]
                    twostop_itn['regional'] = 1 if (first_leg['regional'].iloc[0] or second_leg['regional'].iloc[0] or third_leg['regional'].iloc[0]) else 0
                    twostop_itn['prop'] = 1 if ((not twostop_itn['regional'].iloc[0]) and (first_leg['prop'].iloc[0] or second_leg['prop'].iloc[0] or third_leg['prop'].iloc[0])) else 0
                    twostop_itn['capacity'] = min(first_leg['capacity'].iloc[0], second_leg['capacity'].iloc[0], third_leg['capacity'].iloc[0])
                    twostop_itn['distance'] = first_leg['distance'].iloc[0] + second_leg['distance'].iloc[0] + third_leg['distance'].iloc[0]
                    twostop_itn['flight_legs'] = [[first_leg['id'].iloc[0], second_leg['id'].iloc[0], third_leg['id'].iloc[0]]]
                    twostop_itn['flight_path'] = city_pair[0] + " -> " + first_leg.dest_iata.iloc[0] + " -> " + second_leg.dest_iata.iloc[0] + " -> " + city_pair[1]
                    twostop_itn['first_transfer_city'] = first_leg.dest_iata.iloc[0]
                    twostop_itn['second_transfer_city'] = second_leg.dest_iata.iloc[0]
                    twostop_itn['city_pair'] = city_pair_str
                    twostop_itn['service_lvl'] = 3
                    twostop_itn['first_layover'] = (second_leg['deprt_time'].iloc[0] - (first_leg['deprt_time'].iloc[0] + first_leg['duration'].iloc[0]))
                    twostop_itn['second_layover'] = (third_leg['deprt_time'].iloc[0] - (second_leg['deprt_time'].iloc[0] + second_leg['duration'].iloc[0]))

                    resultant_itns = pd.concat([resultant_itns, twostop_itn])
                    
            
    return resultant_itns


def get_city_pair_probabilities(city_pair_itns, coefficients, demand=0):
    city_pair_itns.reset_index(drop=True, inplace=True)
    city_pair_itns.drop('id', inplace=True, axis=1)
    city_pair_itns['itn_no'] = range(1, len(city_pair_itns) + 1)
    city_pair_itns['itn_no'] = "ITN_" + city_pair_itns['itn_no'].astype(str)
    
    # ----------- Generating independent variables -----------
    
    # --- Level of service ---
    
    market_type = city_pair_itns.service_lvl.min()
    
    city_pair_itns['nonstop_itn_nonstop_mrkt'] = ((city_pair_itns['service_lvl'] == market_type) & (market_type == 0)).astype(int)
    city_pair_itns['direct_itn_nonstop_mrkt'] = ((city_pair_itns['service_lvl'] == 1) & (market_type == 0)).astype(int)
    city_pair_itns['single_itn_nonstop_mrkt'] = ((city_pair_itns['service_lvl'] == 2) & (market_type == 0)).astype(int)
    city_pair_itns['double_itn_nonstop_mrkt'] = ((city_pair_itns['service_lvl'] == 3) & (market_type == 0)).astype(int)
    city_pair_itns['direct_itn_direct_mrkt'] = ((city_pair_itns['service_lvl'] == market_type) & (market_type == 1)).astype(int)
    city_pair_itns['single_itn_direct_mrkt'] = ((city_pair_itns['service_lvl'] == 2) & (market_type == 1)).astype(int)
    city_pair_itns['double_itn_direct_mrkt'] = ((city_pair_itns['service_lvl'] == 3) & (market_type == 1)).astype(int)
    city_pair_itns['single_itn_single_mrkt'] = ((city_pair_itns['service_lvl'] == market_type) & (market_type == 2)).astype(int)
    city_pair_itns['double_itn_single_mrkt'] = ((city_pair_itns['service_lvl'] == 3) & (market_type == 2)).astype(int)

    # --- Connection quality ---
    
    for transfer_city in city_pair_itns.first_transfer_city.unique().tolist():
        transfer_city_filter = (city_pair_itns['first_transfer_city'] == transfer_city)
        
        second_best_cnct_time = city_pair_itns.loc[transfer_city_filter].first_layover.min()
        
        city_pair_itns.loc[transfer_city_filter, 'second_best_cnct'] = city_pair_itns.loc[transfer_city_filter, 'first_layover'].apply(lambda x: 0 if x == second_best_cnct_time else 1)
        city_pair_itns.loc[transfer_city_filter, 'second_best_cnct_time_diff'] = city_pair_itns.loc[transfer_city_filter, 'first_layover'] - second_best_cnct_time
    
    best_cnct_time = city_pair_itns.loc[city_pair_itns['first_layover'] != 0].first_layover.min()
    city_pair_itns.loc[city_pair_itns['first_layover'] != 0, 'best_cnct_time'] = city_pair_itns.loc[city_pair_itns['first_layover'] != 0, 'first_layover'] - best_cnct_time

    shortest_distance = city_pair_itns.distance.min()
    city_pair_itns['distance_ratio'] = (city_pair_itns['distance'] / shortest_distance) * 100

    # --- Aircraft size & type ---
    
    # If itn is not regional nor prop, it is mainline:
    city_pair_itns['mainline'] = (~(city_pair_itns['prop'] | city_pair_itns['regional'])).astype(int)
    # Get mainline seats if no regional/prop aircraft in itn:
    city_pair_itns['mainline_seats'] = city_pair_itns['mainline'] * city_pair_itns['capacity']
    # Get regional seats only if no propeller aircraft in itn:
    city_pair_itns['regional_seats'] = city_pair_itns['regional'] * (1 - city_pair_itns['prop']) * city_pair_itns['capacity']
    # If there's a prop in itn, get seats:
    city_pair_itns['prop_seats'] = city_pair_itns['prop'] * city_pair_itns['capacity']
    
    # --- Time of day ---
    
    city_pair_itns['midn_to_5'] = city_pair_itns['deprt_time'].between(time_to_dt("00:00"), time_to_dt("05:00"), inclusive='left').astype(int)

    for hr in range(5, 22):
        city_pair_itns[f"{hr}_to_{hr+1}"] = city_pair_itns['deprt_time'].between(time_to_dt(f"{hr}:00"), time_to_dt(f"{hr+1}:00"), inclusive='left').astype(int)
    
    city_pair_itns['22_to_midn'] = city_pair_itns['deprt_time'].between(time_to_dt("22:00"), time_to_dt("23:59"), inclusive='left').astype(int)
    
    # ----------- Generating probabilities -----------
    
    city_pair_itns['second_best_cnct_time_diff'] = city_pair_itns['second_best_cnct_time_diff'].dt.seconds / 60
    city_pair_itns['best_cnct_time'] = city_pair_itns['best_cnct_time'].dt.seconds / 60

    coefficients = pd.concat([coefficients]*len(city_pair_itns), ignore_index=True)
    city_pair_itns['itn_score'] = (city_pair_itns[coefficients.columns] * coefficients)[coefficients.columns].sum(axis=1)
    city_pair_itns['exp_score'] = np.exp(city_pair_itns['itn_score'])
    city_pair_itns['probability'] = city_pair_itns['exp_score'] / city_pair_itns['exp_score'].sum()
    city_pair_itns['demand'] = (city_pair_itns['probability'] * demand).round(2)
    
    # ----------- Calculating QSIs -----------
    
    airlines_qsi = city_pair_itns.groupby('airline_iata')['probability'].sum().to_frame()
    airlines_qsi['qsi'] = airlines_qsi['probability'] / airlines_qsi['probability'].sum()
    airlines_qsi['qsi_squared'] = np.square(airlines_qsi['probability'])
    airlines_qsi['demand'] = (airlines_qsi['probability'] * demand).round(2)
    
    hhi_score = airlines_qsi['qsi_squared'].sum()
    
    # ----------- Transpose & Export -----------
    
    # city_pair_itns = city_pair_itns.transpose()
    # city_pair_itns.to_csv('trnsposed.csv')
    
    return city_pair_itns, airlines_qsi, hhi_score


def time_to_dt(timestring):
    """Turns time to datetime object with date set as the dummy date set up in document setup variables.

    Args:
        time (str): Time to be converted to datetime object, formatted as HH:MM.
    """
    return dt.strptime(dummy_date + " " + timestring, "%Y-%m-%d %H:%M")


def generate_all_itineraries(routes_df, airlines):
    cities = get_cities(routes_df)
    city_pairs = get_city_pairs(cities)
    
    resultant_itns = pd.DataFrame()
    
    for city_pair in city_pairs:
        resultant_itns = pd.concat([resultant_itns, get_city_pair_itineraries(routes_df, city_pair, airlines)])
        
    return resultant_itns


def get_demand(city_pair, demands):
    demand = demands[(demands['origin'] == city_pair[0]) & (demands['destination'] == city_pair[1])]['demand']
    if demand.size > 0:
        return demand.iloc[0]
    
    return 0
    
    
def main():
    start_time = time.time()
    
    # Load Data:
    raw_routes_df = pd.read_excel(routes_filename)
    coefficients = pd.read_excel(coefficients_filename).transpose()
    coeffs_headers = coefficients.iloc[0]
    coefficients = pd.DataFrame(coefficients.values[1: ], columns=coeffs_headers)
    demands = pd.read_excel(demands_filename)
    
    # Transformations:
    routes_df = clean_data(raw_routes_df)
    airlines = get_airlines(routes_df)
    
    # ALGO
    city_pair = ["ASW", "SSH"]
    demand = get_demand(city_pair, demands)
        
    cp_itns = get_city_pair_itineraries(routes_df, city_pair, airlines)
    cp_probs = get_city_pair_probabilities(cp_itns, coefficients, demand)
    
    # # Generate all itineraries
    # all_itns = generate_all_itineraries(routes_df, airlines)
    
    # # Print all itineraries to a CSV
    # all_itns.to_csv("all_itns.csv")

    
    print("Process finished --- %s seconds ---" % (time.time() - start_time))
    
    
if __name__ == "__main__":
    main()