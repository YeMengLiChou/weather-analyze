import json
import re
import time

import scrapy
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from config import constants
from utils.redis_utils import RedisUtils


class WrappedRedisSpider(RedisSpider):
    """
    扩展 RedisSpider，用于获取城市信息数据的前置工作
    """

    def __init__(self, redis_config: dict, **kwargs):
        super().__init__(**kwargs)
        self.callback: callable = None
        self.crawler = None
        self.redis = RedisUtils(redis_config)
        self.scraping: bool = False

    def start_prepare(self, callback: callable):
        """
        准备工作
        :return: 准备工作是否完成，True为完成
        """
        self.callback = callback
        # 查询是否有爬虫正在爬取城市信息
        scraping = int(self.redis.get(constants.REDIS_CITY_INFO_SCRAPING, 0)) == 1
        try:
            if not scraping:
                # 设置当前爬虫正在爬取城市信息
                self.redis.set(constants.REDIS_CITY_INFO_SCRAPING, 1)
                # 判断是否已经存在
                contains = int(self.redis.get(constants.REDIS_CITY_INFO_CONTAINS, 0))
                self.scraping = True

                if contains == 0:
                    # 获取城市信息
                    self.logger.info(f'======> 开始爬取城市信息')
                    return [self.__start_scrape_city_info()]
                else:
                    self.logger.info(f'======> 城市信息和id数据存在')
                    return None
            else:
                self.logger.info(f'======> 存在爬虫获取城市信息，等待爬虫完成')
                return None
        finally:
            self.redis.set(constants.REDIS_CITY_INFO_SCRAPING, 0)

    def wait_scraping(self):
        """
        等待爬虫完成
        :return:
        """
        while int(self.redis.get(constants.REDIS_CITY_INFO_SCRAPING, 0)) == 1:
            time.sleep(5)

    def __start_scrape_city_info(self):
        """
        爬取城市信息
        :return:
        """
        return scrapy.Request(
            url='https://tianqi.2345.com/tqpcimg/tianqiimg/theme4/js/global.js?v=20220613',
            callback=self.__parse_city_info,
            dont_filter=True,
            priority=1000
        )

    def __start_scrape_city_id(self):
        """
        爬取城市id
        :return:
        """
        return scrapy.Request(
            url='https://j.i8tq.com/weather2020/search/city.js',
            callback=self.__parse_city_id,
            dont_filter=True,
            priority=1000
        )

    def __parse_city_info(self, response: Response):
        """
        解析城市省级城市信息
        :param response:
        :return:
        """
        lines = response.text.splitlines()[2:9]
        provinces = {}
        for line in lines:
            result = re.findall(r'theProvs\[(\d+)] = "[A-Z] (\w+)"', line)
            for res in result:
                city_id = res[0]  # 网站特有的id
                city_name = res[1]  # 中文名
                provinces[city_id] = city_name

        self.redis.set_cities_sp_id(provinces)
        yield scrapy.Request(
            url='https://tianqi.2345.com/tqpcimg/tianqiimg/theme4/js/citySelectData2.js',
            callback=self.__parse_city_relation,
            dont_filter=True,
            priority=1000,
            meta={'provinces': provinces}
        )

    def __parse_city_relation(self, response: Response):
        """
        解析城市的省市关系
        :param response:
        :return:
        """

        meta = response.meta
        provinces = meta['provinces']
        lines = response.text.splitlines()[1:35]
        # 所有id到name的映射
        all_mapping = []
        for line in lines:
            res = re.match(r"prov\[(\d+)]\s?=\s?'(.+)'", line)
            if res:
                province_id = res.group(1)
                cities_info = res.group(2)
                result = re.findall(r'(\d+)-[A-Z] (\w+)-\d+', cities_info)
                # 该省下面的城市
                cities_id = []
                cities_name = []
                # TODO：已限制爬取省会信息
                # all_mapping.extend(result)
                for city_id, city_name in result:
                    cities_id.append(city_id)
                    cities_name.append(city_name)
                    all_mapping.append((city_id, city_name))
                    # TODO：已限制爬取省会信息
                    self.logger.info(f'=======> {city_id} {city_name} {province_id} {provinces[province_id]}')
                    break
                # 设置该省市关系
                self.redis.set_city_relation_id(province_id, cities_id)
                self.redis.set_city_relation_name(provinces[province_id], cities_name)

        # 保存id
        self.redis.set_cities_sp_id(all_mapping)

        # 信息已经更新完毕，设置状态为已有
        self.logger.info(f"======> 更新城市所需id完成: 共{len(all_mapping)}条数据")
        yield scrapy.Request(
            url='https://j.i8tq.com/weather2020/search/city.js',
            callback=self.__parse_city_id,
            dont_filter=True,
            priority=1000,
            meta={'all_mapping': all_mapping}
        )

    def __parse_city_id(self, response: Response):
        """
        解析城市id信息
        :param response:
        :return:
        """
        sp_id = response.meta.get('all_mapping')
        # 获取 js 代码，也就是数据
        content = json.loads(response.text[16:])
        cities_names = []
        mapping = []
        for province_name, cities in content.items():
            for city_name, value in cities.items():
                city_id = value[city_name]['AREAID']
                cities_names.append(city_name)
                mapping.append((city_id, city_name))

        # 设置城市id
        self.redis.set_cities_id(mapping)

        # 设置两个数据集的交集，确保两个网站爬取的城市一致
        sp_ids = [item[1] for item in sp_id]
        add = [item[1] for item in mapping if item[1] in sp_ids]
        self.redis.add_all_cities(add)

        self.redis.set(constants.REDIS_CITY_INFO_CONTAINS, 1)
        self.logger.info(f"======> 更新城市id数据完成: 共{int(len(mapping))}条数据")
        self.logger.info(f"======> 更新城市关系数据完成: 共{int(len(add))}条数据")
        self.scraping = False
        yield from self.callback()
