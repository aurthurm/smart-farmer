from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.staticfiles.storage import staticfiles_storage
import numpy as np
import pandas as pd
import requests, json
from . import static


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import openmeteo_requests

import requests_cache
from retry_requests import retry


def recommend_helper():

    #train_data = staticfiles_storage.path('stati')
    #train_data = pd.read_csv("{%static crop/files/crop.csv %}")
    train_data = pd.read_csv("https://raw.githubusercontent.com/dphi-official/Datasets/master/crop_recommendation/train_set_label.csv")

    le = LabelEncoder()
    train_data.crop = le.fit_transform(train_data.crop)

    X = train_data.drop('crop', axis=1)
    y = train_data['crop']

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3)

    model = RandomForestClassifier(n_estimators=150)

    model.fit(X_train, y_train)

    return model, le


def recommend(N, P, K, T, H, ph, R):
    A = [N, P, K, T, H, ph, R]

    model, le = recommend_helper()

    S = np.array(A)
    X = S.reshape(1, -1)

    pred = model.predict(X)

    crop_pred = le.inverse_transform(pred)

    return crop_pred[0]

def getCityInfo(city_name):
    api_key = "15e46bb2ab66ccd2c49c545973237381"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    #city_name = input("Enter city name : ")
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    print(x)
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]-273.15
        current_pressure = y["pressure"]
        current_humidiy = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        #print(current_temperature,current_pressure,current_humidiy,weather_description)
        return current_temperature,current_humidiy,current_temperature+100




#print(recommend(17.0000001, 36.000000, 196.00000, 23.871923, 90.499390, 5.882156, 10))

#def index(request):
    #return HttpResponse(recommend(17.0000001, 36.000000, 196.00000, 23.871923, 90.499390, 5.882156, 10))
def index(request):
    #print(recommend(17.0000001, 36.000000, 196.00000, 23.871923, 90.499390, 5.882156, 10))
    return render(request,'crop/index.html')


def about(request):
    return render(request,'crop/about.html')

def prediction(request):
    return render(request,'crop/predict.html')

def schemes(request):
    return render(request,'crop/schemes.html')

#def latestweather(request):
#    return render(request,'crop/weather.html')

def livefeedpage(request):
    return render(request,'crop/404.html')
def community(request):
    return render(request,'crop/404.html')

def contact(request):
    return render(request,'crop/contact.html')

def index1(request):
    if request.method == 'POST':
        try:
            dataa = json.loads(request.POST['content'] )
            print(dataa)
            t1,t2,t3=getCityInfo(dataa[0])

            crop1=recommend(dataa[2],dataa[3],dataa[4], t1, t2, dataa[1], t3)
            print(crop1)
        except:
            crop1="Invalid Input"
            print("Invalid Input")
        #print(type(dataa))
        #return HttpResponse(dataa)
        return JsonResponse({'message': 'success', 'username': "username", 'content': crop1})


def latestweather(request):
    #url = ('https://weatherapi.org/v2/top-headlines?'
    #       'sources=bbc-weather&'
    #       'apiKey=cb2dbc632d8d4eefb8cbf1e87abb2a78')
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)


    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -17.8277,
        "longitude": 31.0534,
        "hourly": ["temperature_2m", "rain"],
        "timezone": "Africa/Cairo"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s"),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["rain"] = hourly_rain

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print(hourly_dataframe)



    return render(request, 'crop/weather.html', context={"mylist": hourly_dataframe})