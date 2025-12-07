import requests

from config import STAR_COST, TRAIN_COST, FORECAST_COST

def calculate_star(star_cost, train_cost, forecast_cost):
    response = requests.get('https://cbu.uz/uz/arkhiv-kursov-valyut/json/')
    print(response.json())


calculate_star(STAR_COST, TRAIN_COST, FORECAST_COST)
