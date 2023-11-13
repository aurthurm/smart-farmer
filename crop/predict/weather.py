import requests


class WeatherPedictor:
    def __init__(self):
        self.API_KEY = "15e46bb2ab66ccd2c49c545973237381"
        self.BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
        
    def _get_url(self, city_name: str):
        return self.BASE_URL + "appid=" + self.API_KEY + "&q=" + city_name


    def get_city_info(self, city_name: str):
        complete_url = self._get_url(city_name)
        
        response = requests.get(complete_url)
        x = response.json()
        
        print(x)
        
        if x["cod"] == "404":
            raise Exception(f"Provided city data not founc {city_name}")


        y = x["main"]
        temp = y["temp"]-273.15
        pressure = y["pressure"]
        humidity = y["humidity"]
        description = x["weather"][0]["description"]
        #print(temp,pressure,humidity,description)
        return temp, humidity, temp+100