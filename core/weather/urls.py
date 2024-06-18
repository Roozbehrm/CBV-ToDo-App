from django.urls import path, include

app_name = "weather"
urlpatterns = [
    path("api/v1/<str:city_name>", include("weather.api.v1.urls")),
]
