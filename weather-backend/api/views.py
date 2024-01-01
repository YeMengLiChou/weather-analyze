from django.http import HttpResponse
from django.shortcuts import render

# from utils import RedisUtils
# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def get_all_cities(request):
    return HttpResponse("You're looking at question")


def get_real_data_by_city_id(request, city_id):
    return HttpResponse(f'{city_id}')