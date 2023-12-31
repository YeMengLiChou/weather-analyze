"""
常量
"""

REDIS_CITY_INFO_CONTAINS = 'city:info:contains'
"""
城市信息是否存在

- & 1 == 1 表示已经存在拼音数据
- & 2 == 2 表示已经存在城市id数据
"""

REDIS_CITY_INFO_SCRAPING = 'city:info:scraping'
"""
城市信息是否有爬虫在获取

- 1 表示有
- 0 表示没有
"""

REDIS_CITY_INFO_NAME_PREFIX = 'city:info:name:'
"""
保存城市拼音数据的前缀
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
保存需要爬取的城市信息
"""


def get_city_info_name_key(city_name: str) -> str:
    """
    获取城市拼音的key

    :param city_name: 城市名称
    :return: 城市拼音数据key
    """
    return REDIS_CITY_INFO_NAME_PREFIX + city_name


def get_city_info_id_key(city_id: str) -> str:
    """
    获取城市id的key

    :param city_id: 城市id
    :return: 城市id数据key
    """
    return REDIS_CITY_INFO_ID_PREFIX + city_id


