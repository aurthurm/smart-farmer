from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import json

import openmeteo_requests

import requests_cache
from retry_requests import retry
from crop.predict import (
    CropRecommender, WeatherPedictor, FertiliserPred
)
from crop.resources.openai import OpenAIGPT

# global gpt so that temporary chat history is maintained
farming_guru = OpenAIGPT() 


def index(request):
    return render(request,'crop/index.html')

def about(request):
    return render(request,'crop/about.html')

def prediction(request):
    return render(request,'crop/predict.html', context={
        "title": "Live Crop Recommendation System",
        "subtitle": "dont guest be smart"
    })

def schemes(request):
    return render(request,'crop/schemes.html')

def contact(request):
    return render(request,'crop/contact.html')

def calculate(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.POST['content'])
            t1, t2, t3 =WeatherPedictor().get_city_info(payload["city"])
            recommended_crop=CropRecommender().recommend(payload["nitrogen"], payload["phosphorous"], payload["potassium"], t1, t2, payload["ph"], t3)
            fert_err, fertiliser_rec = FertiliserPred().recommend(recommended_crop, payload["nitrogen"], payload["phosphorous"], payload["potassium"])
            _recommendation_context = f"""
            The farmer is located in Zimbabwe in the city called {payload["city"]}. 
            His farm recieves an average rainfall of {t3}.
            The temperature is averaging around {t1} degrees celcius.
            From soil analysis it was discovered that nutrient content is as follows:
            Nitrogen {payload["nitrogen"]}, 
            Phosphorous {payload["phosphorous"]},
            Pottasium {payload["potassium"]}
            Ph {payload["ph"]}
            """
            farming_guru.increase_proficiency(_recommendation_context.strip())
            _alternatives = f"""
            Based on the farmers rainfall, soild analysis, a predictive algorithm has recommended that the farmer must 
            concentrate his efforts on "{recommended_crop}". However there might be other types of crops that he can also do. 
            What other crops have a high probability to perform well.
            """
            _, also_consider = farming_guru.chat(_alternatives.strip())
            _, also_consider = farming_guru.chat(_alternatives.strip())
            _fertiser_sugges = f"""
            For the recommended crop {recommended_crop}, a fertiliser recommendation model also noted that {fert_err}. 
            Below are the organic fertiliser recommendations to correct the issue:
            ----------
            {fertiliser_rec}.
            ----------
            What are the synthetic fertiliser recommedations that can be used by the farmer in place  of the organic recommendations? 
            For each synthetic fertilier can you also provide quantities/hectre of land to be applied.
            """
            _, synthetics = farming_guru.chat(_fertiser_sugges.strip())
        except Exception as e:
            recommended_crop= f"some error occured: {e}" + f"{request.POST}"
            also_consider=None
            fertiliser_rec=None
            synthetics=None
            
        return JsonResponse({
            'message': 'success', 
            'content': recommended_crop, 
            "other": also_consider, 
            "fertiliser": fertiliser_rec,
            "synthetics": synthetics
        })

def ask_guru(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.POST['content'])
            role, response = farming_guru.chat(payload["message"])
        except Exception as e:
            role="error"
            response= f"Farm Assistant Guru encuntred an error: {e}" + f"{request.POST}"
        return JsonResponse({'message': 'success', 'data': {"role": role, "content": response}})
    else:
        return render(request,'crop/ask_guru.html', context={
            "title": "Smart Farming Assistant",
            "subtitle": "- ask any farming question -",
            "chats": farming_guru.retrieve_history()
        })

def latestweather(request):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -17.8277,
        "longitude": 31.0534,
        "hourly": ["temperature_2m", "rain"],
        "timezone": "Africa/Cairo"
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
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

    return render(request, 'crop/weather.html', context={"mylist": hourly_dataframe})
