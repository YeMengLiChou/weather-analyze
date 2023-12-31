import json
import threading
from typing import Any

import redis

from config import constants


class RedisUtils(object):
    # 单例模式
    __redis_conn = None

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, config) -> None:
        self.config = config
        self.__redis_conn = redis.StrictRedis(**config)

    def __getstate__(self):
        """
        解决 pickle 无法序列化自定义的问题
        :return:
        """
        return self.config

    def __setstate__(self, state):
        self.__init__(state)

    def close(self):
        self.__redis_conn.close()

    def set(self, key, value):
        """
        设置键的值
        :param key:
        :param value:
        :return:
        """
        self.__redis_conn.set(key, json.dumps(value, ensure_ascii=False))

    def sets(self, mapping: dict | list[tuple[str, Any]]):
        """
        设置一系列键值对
        :param mapping:
        :return:
            """
        if isinstance(mapping, dict):
            for key, value in mapping.items():
                mapping[key] = json.dumps(value, ensure_ascii=False)
            self.__redis_conn.mset(mapping=mapping)
        else:
            result = dict()
            for item in mapping:
                key, value = item
                result[key] = json.dumps(value, ensure_ascii=False)
            self.__redis_conn.mset(mapping=result)

    def get(self, key, default=None):
        """
        获取键的值
        :param key:
        :param default
        :return:
        """
        value: str | None = self.__redis_conn.get(key)
        if value:
            return json.loads(value)
        else:
            return default

    def gets(self, keys: list[str]):
        """
        获取多个key对应的值
        :param keys:
        :return:
        """
        return self.__redis_conn.mget(keys)

    def set_hash(self, key: str, field: str, value):
        """
        设置key对应的hash表中field的值
        :param key:
        :param field:
        :param value:
        :return:
        """
        value = json.dumps(value, ensure_ascii=False)
        return self.__redis_conn.hset(key, field, value)

    def sets_hash(self, key, fields: dict):
        """
        设置key对应的hash表中多个field的值
        :param key:
        :param fields:
        :return:
        """

        for field, value in fields.items():
            fields[field] = json.dumps(value, ensure_ascii=False)
        return self.__redis_conn.hset(key, mapping=fields)

    def get_hash(self, key, field):
        """
        获取key对应的hash表中field的值
        :param key:
        :param field:
        :return:
        """
        value = self.__redis_conn.hget(key, field)
        return json.loads(value)

    def add_set(self, key: str, value: list[str] | str):
        """

        :param key:
        :param value:
        :return:
        """
        if isinstance(value, str):
            self.__redis_conn.sadd(key, value)
        else:
            for i in range(len(value)):
                value[i] = json.dumps(value[i], ensure_ascii=False)
            self.__redis_conn.sadd(key, *value)

    def get_set(self, key):
        """
        获取key对应的set集合中的所有值
        :param key:
        :return:
        """
        result = list(map(lambda x: json.loads(x), self.__redis_conn.smembers(key)))
        return result

    def remove_set(self, key, values: list[str]):
        """
        删除指定set的元素
        :param key:
        :param values:
        :return:
        """
        values = list(map(lambda x: json.dumps(x, ensure_ascii=False), values))
        self.__redis_conn.srem(key, *values)

    def keys(self, pattern: str):
        """
        获取 pattern 匹配的键值
        :param pattern:
        :return:
        """
        return list(map(lambda x: x.decode('utf-8'), self.__redis_conn.keys(pattern)))

    def get_kafka_offset(self, topic: str, partition: int, groupId: str = None) -> int | None:
        value = self.get(f'kafka-{topic}{partition}-{groupId if groupId else ""}')
        if value:
            return int(value)
        else:
            return None

    def set_kafka_offset(self, topic: str, partition: int, groupId: str = None, offset: int = 0):
        self.set(f'kafka-{topic}{partition}-{groupId if groupId else ""}', offset)

    def set_city_pinyin(self, chinese: str, pinyin: str):
        """
        设置城市中文和拼音的对应关系
        :param chinese:
        :param pinyin:
        :return:
        """
        self.sets([
            (constants.get_city_info_name_key(chinese), pinyin),
            (constants.get_city_info_name_key(pinyin), chinese)
        ])

    def get_city_pinyin(self, chinese: str) -> str | None:
        """
        获取城市中文和拼音的对应关系
        :param chinese:
        :return: pinyin
        """
        value = self.get(constants.get_city_info_name_key(chinese))
        if value:
            return value
        else:
            return None

    def get_city_chinese(self, pinyin: str) -> str | None:
        """
        根据 pinyin 获取对应城市的中文名称
        :param pinyin:
        :return: chinese
        """
        value = self.get(constants.get_city_info_name_key(pinyin))
        if value:
            return value
        else:
            return None

    def get_cities_chinese(self, pinyins: list[str]) -> list[str]:
        """
        根据 pinyins 获取对应城市的中文名称
        :param pinyins:
        :return: chinese
        """
        keys = [constants.get_city_info_name_key(pinyin) for pinyin in pinyins]
        return self.gets(keys)

    def set_city_relation(self, province_name: str, cities_name: list[str]):
        """s
        设置城市关系，市级城市->省级城市（拼音）
        :param province_name:
        :param cities_name: 所属市级城市列表
        :return:
        """
        result = {}
        for city_name in cities_name:
            result[city_name] = province_name
        self.sets_hash(constants.REDIS_CITY_INFO_RELATION, result)

    def get_city_province(self, city_name: str, is_pinyin: bool = True) -> str | None:
        """
        获取城市所在省份
        :param city_name:
        :param is_pinyin: 是否为拼音
        :return:
        """
        # 获取对应的拼音
        if not is_pinyin:
            city_name = self.get_city_pinyin(city_name)
        if not city_name:
            return None

        value = self.get_hash(constants.REDIS_CITY_INFO_RELATION, city_name)
        return value

    def set_cities_id(self, mapping: list[tuple[str, str]]):
        """
        设置城市id
        :param mapping: 城市->id
        :return:
        """
        result = []
        for item in mapping:
            result.append((constants.get_city_info_id_key(item[0]), item[1]))
        self.sets(result)

    def get_city_id(self, city_name: str) -> str | None:
        """
        根据拼音或者中文获取城市id，根据城市id获取拼音
        :param city_name:
        :return:
        """
        return self.get(constants.get_city_info_id_key(city_name))

    def get_cities_id(self, cities: list[str]) -> list[str] | None:
        """
        根据拼音或者中文获取城市id，根据城市id获取拼音
        :param cities: 中文pinyin都可以
        :return:
        """
        keys = [constants.get_city_info_id_key(city) for city in cities]
        values = self.gets(keys)
        if values:
            return [value.decode('utf-8')[1:-1] for value in values]
        return values

    def add_all_cities(self, cities: list[str]):
        """
        添加城市信息到所有城市中
        :param cities:
        :return:
        """
        self.add_set(constants.REDIS_CITY_ALL_KEY, cities)

    def get_all_cities(self) -> list[str]:
        """
        获取所有城市的拼音
        :return:
        """
        return self.get_set(constants.REDIS_CITY_ALL_KEY)

    def remove_cities(self, cities: list[str]):
        """
        删除指定的 cities
        :param cities:
        :return:
        """
        self.remove_set(constants.REDIS_CITY_ALL_KEY, cities)
