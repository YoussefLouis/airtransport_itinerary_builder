from flask import Flask, render_template, request
import pandas as pd
import itinerary_builder as ib
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


app = Flask(__name__)

routes_filename = "routes.xlsx"
coefficients_filename = "coefficients.xlsx"
demands_filename = "demands.xlsx"
routes_df = pd.DataFrame()
coefficients = pd.DataFrame()
demands = pd.DataFrame()
cities = []
airlines = []
city_pairs = []

@app.before_first_request
def setup_data():
    global cities, airlines, routes_df, city_pairs, coefficients, demands
    
    # Load Data:
    raw_routes_df = pd.read_excel(routes_filename)
    coefficients = pd.read_excel(coefficients_filename).transpose()
    coeffs_headers = coefficients.iloc[0]
    coefficients = pd.DataFrame(coefficients.values[1: ], columns=coeffs_headers)
    demands = pd.read_excel(demands_filename)
    
    # Transformations:
    routes_df = ib.clean_data(raw_routes_df)
    airlines = ib.get_airlines(routes_df)
    cities = ib.get_cities(routes_df)
    city_pairs = ib.get_city_pairs(cities)
        

@app.route('/', methods=['GET', 'POST'])
def home_screen():
    global routes_df, coefficients, demands
    
    error = None
    itn_prbs = pd.DataFrame()
    qsis = pd.DataFrame()
    hhi = 0
    demand = 0
    
    if request.method == "POST":
        first_city = request.form['first_city']
        second_city = request.form['second_city']

        if [first_city, second_city] in city_pairs:
            demand = ib.get_demand([first_city, second_city], demands)
            
            try:
                cp_itns = ib.get_city_pair_itineraries(routes_df, [first_city, second_city], airlines)
                itn_prbs, qsis, hhi = ib.get_city_pair_probabilities(cp_itns, coefficients, demand)
                
        
                itn_prbs['probability'] = (itn_prbs['probability'] * 100).round(2)
                qsis['Airline'] = qsis.index
                qsis['probability'] = (qsis['probability'] * 100).round(2)
                
                draw_itn_prbs = itn_prbs.set_index('itn_no')
                draw_itn_prbs['probability'].plot(kind="pie", title='Itineraries', y='probability', figsize=(3,3), legend=True, cmap='viridis', labeldistance=None)
                plt.savefig('static/itns_pie.png', bbox_inches='tight')
                # plt.show()
                plt.close()
                
                qsis['probability'].plot(kind="pie", figsize=(3,3), title='Airline QSIs', y='probability', legend=True, cmap='viridis', labeldistance=None)
                plt.savefig('static/qsis_pie.png', bbox_inches='tight')
                # plt.show()
                plt.close()
            except:
                error = "No itineraries found between selected city pair."
        else:
            error = "No itineraries found between selected city pair."
            
    
    
    return render_template(
        "home.html",
        cities = cities,
        itn_prbs_columns = itn_prbs.columns.tolist(),
        itn_prbs = itn_prbs.values.tolist(), 
        qsis_columns = qsis.columns.tolist(),
        qsis = qsis.values.tolist(), 
        hhi = round(hhi, 3),
        error = error,
        demand = demand
        )
