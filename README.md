# Air Transport Market Itinierary Builder

The itinerary builder is a tool to calculate all possible air travel itineraries from a given list of flights in an air transport market. The output of the algorithm is all possible itineraries across the cities of the market, and the probability that a traveller would choose an itinerary over the other available ones across a city pair, where a city pair is the origin city and destination city of the traveller. The algorithm also calculates the probability that an airline is picked by the traveller over others across a city pair, given their offered itineraries, the Quality of Service Index (QSI) of the airlines and the Herfindahl–Hirschman index of the city pair.

This is implemented in Python functions and a Flask web interface. 

Inputs required are:
- CSV with all flights in market with sufficient independent variables
- CSV with coefficients of matching independent variables for the utility function that calculates the itinerary probabilities, those coefficients can be generated using a Multinomial Logistic Regression model
- (optional) CSV with demands estimated across market city pairs, to calculate demands as well as the probabilities
