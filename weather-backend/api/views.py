import json
import os
import sys
from django.http import HttpResponse, JsonResponse

# 获取当前文件所在目录的绝对路径
current_path: str = os.path.abspath(os.path.dirname(__file__))
import_path = current_path.rsplit(os.sep, 2)[0]
# 将目录的绝对路径添加到sys.path中
sys.path.append(import_path)

from utils.redis_utils import RedisUtils
from config.config import REDIS_CONFIG
from .models import RealData, HistoryData

__redis = RedisUtils(config=REDIS_CONFIG)


def to_json(obj):
    if isinstance(obj, dict):
        return obj
    return dict([(key, obj.__dict__[key]) for key in obj.__dict__.keys() if key != '_state'])


def __generate_json(code: int, msg: str, data: dict):
    """
    生成json格式的响应
    :param code:
    :param msg:
    :param data:
    :return:
    """
    response = {
        'code': code,
        'msg': msg,
        'data': to_json(data)
    }
    # return HttpResponse(
    #     json.dumps(response, ensure_ascii=False,default=lambda o: o.__dict__ ),
    #     content_type='application/json'
    # )
    return response


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def get_all_cities(request):
    """
    返回所有城市，省： {市级:id}
    :param request:
    :return:
    """
    all_cities = __redis.get_all_cities()
    all_ids = __redis.get_cities_id(all_cities)
    relations = __redis.get_all_cities_provinces()
    result = {}
    for city, city_id in zip(all_cities, all_ids):
        if city in relations:
            province = relations[city]
            if province not in result:
                result[province] = {}
            result[province][city] = city_id
    return JsonResponse(__generate_json(200, 'success', result))


def get_real_data_by_city_id(request, city_id):
    """
    通过city_id返回对应的实时天气
    :param request:
    :param city_id:
    :return:
    """
    city_name = __redis.get_city_id(city_id)
    try:
        item = RealData.objects.filter(city_name=city_name).get()
        print(item)
        return JsonResponse(__generate_json(200, 'success', item))
    except RealData.DoesNotExist:
        # return __generate_json(404, 'city not found', {})
        return JsonResponse(__generate_json(400, 'no city', {}))


# def get_all_real_data(request):
