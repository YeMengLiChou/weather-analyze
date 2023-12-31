import json
from typing import Generator

import scrapy
from scrapy.crawler import Crawler
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider
from abc import ABCMeta

from utils.redis_utils import RedisUtils
from config import constants


class WrappedRedisSpider(RedisSpider):
    """
    扩展 RedisSpider，用于获取城市信息数据的前置工作
    """

    def __init__(self, redis_config: dict, **kwargs):
        super().__init__(**kwargs)
        self.callback = None
        self.crawler = None
        self.redis = RedisUtils(redis_config)
        self.scraping = False

    def start_prepare(self, callback: callable = None):
        """
        准备工作
        :return: 准备工作是否完成，True为完成
        """
        # 查询是否有爬虫正在爬取城市信息
        scraping = int(self.redis.get(constants.REDIS_CITY_INFO_SCRAPING, 0)) == 1
        self.callback = callback
        try:
            if scraping == 0:
                # 设置当前爬虫正在爬取城市信息
                self.redis.set(constants.REDIS_CITY_INFO_SCRAPING, 1)
                # 判断是否已经存在
                contains = int(self.redis.get(constants.REDIS_CITY_INFO_CONTAINS, 0))

                if contains == 2:
                    self.logger.info(f'======> 城市信息和id数据存在')
                    callback()
                elif contains == 1:
                    self.logger.info(f'======> 城市信息存在，城市id缺失，开始爬取城市id')
                    return [self.__start_scrape_city_id()]
                else:
                    # 获取城市信息
                    self.logger.info(f'======> 城市信息缺失，开始爬取城市信息')
                    return [self.__start_scrape_city_info()]
            else:
                self.logger.info(f'======> 存在爬虫获取城市信息，等待爬虫完成')
                callback()
                return None
        finally:
            self.redis.set(constants.REDIS_CITY_INFO_SCRAPING, 0)

    def __start_scrape_city_info(self):
        """
        爬取城市信息
        :return:
        """
        return scrapy.Request(url='https://www.tianqi.com/chinacity.html',
                              callback=self.__parse_city_info,
                              dont_filter=True)

    def __start_scrape_city_id(self):
        """
        爬取城市id
        :return:
        """
        return scrapy.Request(url='https://j.i8tq.com/weather2020/search/city.js',
                              callback=self.__parse_city_id,
                              dont_filter=True)
        # yield request

    def __parse_city_info(self, response: Response):
        """
        解析城市信息，会调用 __parse_city_id
        :param response:
        :return:
        """
        citybox = response.css('.citybox')
        h2 = citybox.css('h2')
        span = citybox.css('span')
        provinces = zip(h2, span)
        count = 0
        for province, cities in provinces:
            href: str = province.css('a::attr(href)').get()
            chinese_name: str = province.css('::text').get()
            index = href.find('/province/')
            if index == -1:
                # 没有市级城市，需要把省份城市加入
                province_pinyin = href[1:-1]  # 去掉'/'
                self.redis.set_city_pinyin(chinese_name, province_pinyin)
                self.redis.set_city_relation(province_pinyin, [province_pinyin])
            else:
                # 处理省级城市
                province_pinyin = href[10:-1]  # 去掉 '/province/'
                if chinese_name.find('省') == -1:  # 如果没有 '省'，则加上 '省'
                    chinese_name = chinese_name + '省'
                self.redis.set_city_pinyin(chinese_name, province_pinyin)
                # 处理市级城市
                result = []
                for city in cities.css('h3 a'):
                    city_name = city.css('::text').get()
                    city_pinyin = city.css('::attr(href)').get()[1:-1]
                    self.redis.set_city_pinyin(city_name, city_pinyin)
                    result.append(city_pinyin)

                # 保存城市关系
                self.redis.set_city_relation(province_pinyin, result)
                self.redis.add_all_cities(result)
                count += len(result)

        # 信息已经更新完毕，设置状态为已有
        self.logger.info(f"======> 更新城市拼音数据完成: 共{count}条数据")
        self.redis.set(constants.REDIS_CITY_INFO_CONTAINS, 1)

        # 开始获取城市id
        yield scrapy.Request(url='https://j.i8tq.com/weather2020/search/city.js',
                             callback=self.__parse_city_id,
                             dont_filter=True)

    def __parse_city_id(self, response: Response):
        """
        解析城市id信息
        :param response:
        :return:
        """
        # 获取 js 代码，也就是数据
        content = json.loads(response.text[16:])
        result = []
        content_cities = []
        remove_cities = []
        for province_name, cities in content.items():
            for city_name, value in cities.items():
                city_id = value[city_name]['AREAID']

                pinyin = self.redis.get_city_pinyin(city_name)
                # 没有对应的拼音，可能是包含了其他字，使用正则匹配
                if not pinyin:
                    keys = self.redis.keys(constants.get_city_info_name_key(f'{city_name}*'))
                    for key in keys:
                        pinyin = self.redis.get_city_pinyin(key)
                if pinyin:
                    result.append((pinyin, city_id))
                    result.append((city_name, city_id))
                    result.append((city_id, pinyin))
                    content_cities.append(pinyin)

        # 删除没有对应id的城市
        all_cities_pinyin = self.redis.get_all_cities()
        for city_pinyin in all_cities_pinyin:
            if city_pinyin not in content_cities:
                remove_cities.append(city_pinyin)
        self.redis.remove_cities(remove_cities)

        # 设置城市id
        self.redis.set_cities_id(result)
        self.redis.set(constants.REDIS_CITY_INFO_CONTAINS, 2)
        self.logger.info(f"======> 更新城市id数据完成: 共{int(len(result) / 3)}条数据")
        self.__check_scraping()

    def __check_scraping(self):
        """
        检查爬虫状态
        :return:
        """
        if self.scraping:
            self.logger.info('======> 已经完成城市信息和id数据爬取')
            self.scraping = False
            if self.callback:
                self.callback()
