from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cities/", views.get_all_cities, name="cities"),
    path("real/<str:city_id>/", views.get_real_data_by_city_id, name="real"),
    path("real/all/", views.get_all_real_data, name="real_all"),
    path("history/", views.get_history_data_by_city_id, name="history"),
    path("cityname/<str:city_id>", views.get_city_name_by_id, name="cityname" )
]