"""
常量
"""

REDIS_CITY_INFO_CONTAINS = 'city:info:contains'
"""
城市信息是否存在
- 0：
"""

REDIS_CITY_INFO_SCRAPING = 'city:info:scraping'
"""
城市信息是否有爬虫在获取

- 1 表示有
- 0 表示没有
"""

REDIS_CITY_INFO_SPID_PREFIX = 'city:info:spid:'
"""
保存城市特殊id的前缀
"""

REDIS_CITY_INFO_RELATION = 'city:info:relation'
"""
保存省级城市与其市级城市的前缀
"""

REDIS_CITY_INFO_ID_PREFIX = 'city:info:id:'
"""
保存城市id数据的前缀
"""

REDIS_CITY_ALL_KEY = 'city:info:all'
"""
保存需要爬取的城市id信息
"""

REDIS_HISTORY_TIME_KEY = 'history:time:'
"""
历史数据的最新日期
"""


DATA_TYPE_REAL = 1
"""
实时数据
"""

DATA_TYPE_HISTORY = 2
"""
历史数据
"""

DATA_TYPE_FORCAST = 3
"""
预测数据    
"""


def get_city_info_spid_key(city_name: str) -> str:
    """
    获取城市网站特殊id的key

    :param city_name: 城市名称
    :return: 城市拼音数据key
    """
    return REDIS_CITY_INFO_SPID_PREFIX + city_name


def get_city_info_id_key(city_id: str) -> str:
    """
    获取城市id的key

    :param city_id: 城市id
    :return: 城市id数据key
    """
    return REDIS_CITY_INFO_ID_PREFIX + city_id


def get_history_time_key(city_name) -> str:
    """
    获取历史数据最新日期的key

    :param city_name
    :param date
    :return: 历史数据最新日期的key
    """
    return f'{REDIS_HISTORY_TIME_KEY}{city_name}'
