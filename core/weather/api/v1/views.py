import requests
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response


class WeatherAPIView(APIView):
    @method_decorator(cache_page(60 * 20))
    def get(self, request, city_name):
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid=ef9e83a4fdac3ef5ac9e515ffb726f83"
        weather = requests.get(weather_url)
        return Response(weather.json())
