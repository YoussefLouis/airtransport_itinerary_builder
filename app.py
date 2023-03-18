from flask import Flask, render_template, request, make_response
import pandas as pd
import itinerary_builder as ib

app = Flask(__name__)

routes_filename = "routes.xlsx"
coefficients_filename = "coefficients.xlsx"
routes_df = pd.DataFrame()
cities = []
airlines = []
city_pairs = []

@app.before_first_request
def setup_data():
    global cities, airlines, city_pairs, routes_df
    
    # Load Data:
    raw_routes_df = pd.read_excel(routes_filename)
    coefficients = pd.read_excel(coefficients_filename).transpose()
    coeffs_headers = coefficients.iloc[0]
    coefficients = pd.DataFrame(coefficients.values[1: ], columns=coeffs_headers)
    
    # Transformations:
    routes_df = ib.clean_data(raw_routes_df)
    airlines = ib.get_airlines(routes_df)
    cities = ib.get_cities(routes_df)
    city_pairs = ib.get_city_pairs(cities)
    
    
@app.route('/', methods=['GET', 'POST'])
def home_screen():
    
    return render_template(
        "home.html",
        city_pairs = city_pairs
        )
