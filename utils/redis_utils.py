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

    def set_cities_sp_id(self, items: list[tuple[str, str]] | dict[str, str]):
        """
        设置城市特殊的id（2345天气网特有的）
        :param items: id->城市
        :return:
        """
        if isinstance(items, dict):
            items = items.items()
        mapping = {}
        for item in items:
            mapping[constants.get_city_info_spid_key(item[0])] = item[1]
            mapping[constants.get_city_info_spid_key(item[1])] = item[0]
        self.__redis_conn.mset(mapping)

    def get_city_spid_by_name(self, city_name: str) -> str | None:
        """
        获取城市的特殊id
        :param city_name:
        :return:
        """
        value = self.__redis_conn.get(constants.get_city_info_spid_key(city_name))
        return value.decode()

    def get_cities_spid_by_name(self, cities_name: list[str]) -> list[str] | None:
        """
        获取城市的特殊id
        :param cities_name:
        :return:
        """
        keys = [constants.get_city_info_spid_key(city_name) for city_name in cities_name]
        values = [value.decode('utf-8') for value in self.__redis_conn.mget(keys)]
        if len(values) > 0:
            return values
        return None

    def get_city_name_by_spid(self, city_id: str) -> str | None:
        """
        获取城市的名字
        :param city_id:
        :return:
        """
        value = self.__redis_conn.get(constants.get_city_info_spid_key(city_id))
        return value.decode()

    def set_city_relation_id(self, province_id: str, cities_id: list[str]):
        """s
        设置城市关系，市级城市->省级城市 (id -> id)
        :param province_id:
        :param cities_id: 所属市级城市列表
        :return:
        """
        result = {}
        for city_id in cities_id:
            result[city_id] = province_id
        self.sets_hash(constants.REDIS_CITY_INFO_RELATION, result)

    def set_city_relation_name(self, province_name: str, cities_name: list[str]):
        """s
        设置城市关系，市级城市->省级城市 (name -> name)
        :param province_name:
        :param cities_name: 所属市级城市列表
        :return:
        """
        result = {}
        for name in cities_name:
            result[name] = province_name
        self.sets_hash(constants.REDIS_CITY_INFO_RELATION, result)

    def get_city_province(self, city_name: str) -> str | None:
        """
        获取城市所在省份,id和中文都可,id->id, name->name
        :param city_name:
        :return:
        """
        value = self.get_hash(constants.REDIS_CITY_INFO_RELATION, city_name)
        return value.decode()

    def get_all_cities_provinces(self):
        """
        获取城市所在省份,id和中文都可,id->id, name->name
        :param cities:
        :return:
        """
        values = self.__redis_conn.hgetall(constants.REDIS_CITY_INFO_RELATION)
        result = {}
        for key, value in values.items():
            result[key.decode()] = value.decode()
        return result


    def set_cities_id(self, mapping: list[tuple[str, str]]):
        """
        设置城市id
        :param mapping: 城市->id
        :return:
        """
        result = []
        for item in mapping:
            result.append((constants.get_city_info_id_key(item[0]), item[1]))
            result.append((constants.get_city_info_id_key(item[1]), item[0]))
        self.sets(result)

    def get_city_id(self, city_name: str) -> str | None:
        """
        根据中文获取城市id，或根据城市id获取中文名字
        :param city_name:
        :return:
        """
        return self.get(constants.get_city_info_id_key(city_name))

    def get_cities_id(self, cities: list[str]) -> list[str] | None:
        """
        根据中文获取城市id，根据城市id获取拼音
        :param cities:
        :return:
        """
        keys = [constants.get_city_info_id_key(city) for city in cities]
        values = self.gets(keys)
        return [value.decode('utf-8')[1:-1] for value in values]

    def add_all_cities(self, cities: list[str]):
        """
        添加城市名称到所有城市中
        :param cities:
        :return:
        """
        self.__redis_conn.sadd(constants.REDIS_CITY_ALL_KEY, *cities)

    def get_all_cities(self) -> list[str]:
        """
        获取所有城市名称
        :return:
        """
        return list(map(lambda x: x.decode('utf-8'), self.__redis_conn.smembers(constants.REDIS_CITY_ALL_KEY)))

    def remove_cities(self, cities_id: list[str]):
        """
        删除指定的 cities 的 id
        :param cities_id:
        :return:
        """
        self.__redis_conn.srem(constants.REDIS_CITY_ALL_KEY, *cities_id)
