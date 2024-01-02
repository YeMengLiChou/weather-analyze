from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cities/", views.get_all_cities, name="cities"),
    path("real/<str:city_id>/", views.get_real_data_by_city_id, name="real")
]