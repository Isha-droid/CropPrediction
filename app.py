
from flask import Flask, render_template, request, Markup, jsonify
import numpy as np
import pandas as pd
import requests
from utils.fertilizer import fertilizer_dic
import config
import pickle
import io

crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = pickle.load(open(crop_recommendation_model_path, 'rb'))

def weather_fetch(city_name):
    
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]
        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None

app = Flask(__name__)

# render home page





@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():

    if request.method == 'POST':
        N = int(request.form.get('nitrogen'))
        P = int(request.form.get('phosphorous'))
        K = int(request.form.get('pottasium'))
        # temperature = int(request.form.get('temperature'))
        # humidity= int(request.form.get('humidity'))
        ph = float(request.form.get('ph'))
        rainfall = float(request.form.get('rainfall'))
        city = str(request.form.get("city"))
        if weather_fetch(city) != None:
           temperature, humidity = weather_fetch(city)
           data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
           my_prediction = crop_recommendation_model.predict(data)
           final_prediction = my_prediction[0]
           return jsonify({'crop':final_prediction})
        else:
           return jsonify("Enter valid city name ")


@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    crop_name = str(request.form.get('cropname'))
    N = int(request.form.get('nitrogen')) #available
    P = int(request.form.get('phosphorous'))
    K = int(request.form.get('pottasium'))

    df = pd.read_csv('Data/fertilizer.csv')
    nr = df[df['Crop'] == crop_name]['N'].iloc[0] #required
    pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    kr = df[df['Crop'] == crop_name]['K'].iloc[0]
    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"

    response = str(fertilizer_dic[key])

    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0")
