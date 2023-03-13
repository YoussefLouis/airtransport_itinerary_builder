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
            price_usd

"""

import pandas as pd
import numpy as np
import csv 


# Setup:
routes_filename = "routes_manual.xlsx"
hardcoded_cities = ["CAI", "ASW", "HUR", "CAI"]


def get_city_pairs(cities):
    city_pairs = []
    for first_city in cities:
        for second_city in cities:
            if first_city != second_city:
                if [first_city, second_city] not in city_pairs:
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
    
    
def main():
    # Load Data:
    routes_df = pd.read_excel(routes_filename)
    cities = get_cities(routes_df)
    airlines = get_airlines(routes_df)
    city_pairs = get_city_pairs(cities)
    
    city_pair_itns = {}
    
    for city_pair in city_pairs[0:2]:
        city_pair_str = city_pair[0] + "_" + city_pair[1]
        city_pair_itns[city_pair_str] = pd.DataFrame()
        
        for airline in airlines:
            airline_itns = routes_df[routes_df['airline_iata'] == airline]
            routes_with_origin = airline_itns[airline_itns['origin_iata'] == city_pair[0]]
            nonstop_itns = routes_with_origin[routes_with_origin['dest_iata'] == city_pair[1]]

            other_routes = routes_with_origin[~ routes_with_origin['id'].isin(nonstop_itns.id)]
            
            for other_route in other_routes.itertuples():
                
            
            valid_itns = nonstop_itns

            city_pair_itns[city_pair_str] = pd.concat([city_pair_itns[city_pair_str], valid_itns])
        
    # print(city_pair_itns)
    
    
if __name__ == "__main__":
    main()