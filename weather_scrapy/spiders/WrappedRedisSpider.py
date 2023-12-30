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
        self.scraping = 0
        self.city_info_scraping = False
        self.city_id_scraping = False

    def start_prepare(self, callback: callable = None):
        """
        准备工作
        :return: 准备工作是否完成，True为完成
        """
        scraping = int(self.redis.get(constants.REDIS_CITY_INFO_SCRAPING, 0))
        self.callback = callback
        try:
            result = []
            if scraping == 0:
                # 当前爬虫正在爬取信息
                self.redis.set(constants.REDIS_CITY_INFO_SCRAPING, 1)
                # 判断是否已经存在
                contains = self.redis.get(constants.REDIS_CITY_INFO_CONTAINS, 0)

                if not (contains & 1 == 1):
                    # 获取城市信息
                    self.logger.info(f'======> 城市信息缺失，开始爬取城市信息')
                    self.city_info_scraping = True
                    result.append(self.__start_scrape_city_info())
                if not ((contains >> 1) & 1 == 1):
                    # 获取城市id
                    self.logger.info(f'======> 城市id数据缺失，开始爬取城市id')
                    self.city_id_scraping = True
                    result.append(self.__start_scrape_city_id())

                if contains & 1 == 1 and contains >> 1 & 1 == 1:
                    self.logger.info(f'======> 城市信息和id数据存在')
                    callback()
            else:
                self.logger.info(f'======> 城市信息和id数据存在')
                callback()
            return result
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
        return scrapy.Request(url='https://blog.csdn.net/qq_42855293/article/details/103864266',
                              callback=self.__parse_city_id,
                              dont_filter=True)

    def __parse_city_info(self, response: Response):
        """
        解析城市信息
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
        status = self.redis.get(constants.REDIS_CITY_INFO_CONTAINS, 0) | 1
        self.redis.set(constants.REDIS_CITY_INFO_CONTAINS, status)
        self.__check_scraping()
        self.logger.info(f"======> 更新城市拼音数据完成: 共{count}条数据")

    def __parse_city_id(self, response: Response):
        # 获取中间的表格
        table_rows = response.xpath('//div[@id="content_views"]//table/tbody/tr')
        result = []
        # 遍历表格的每一行
        for row in table_rows:
            tds = row.css('td')
            if len(tds) == 4:
                city_id = tds[3].css('::text')
                city_name = tds[2].css('::text')
                result.append((city_name.get(), city_id.get()))

        self.redis.set_cities_id(result)
        status = self.redis.get(constants.REDIS_CITY_INFO_CONTAINS, 0) | 2
        self.redis.set(constants.REDIS_CITY_INFO_CONTAINS, status)
        self.__check_scraping()
        self.logger.info(f"======> 更新城市id数据完成: 共{len(result)}条数据")

    def __check_scraping(self):
        """
        检查爬虫状态
        :return:
        """
        if not self.city_info_scraping and not self.city_id_scraping:
            self.logger.info('======> 已经完成城市信息和id数据爬取')
            self.redis.set(constants.REDIS_CITY_INFO_SCRAPING, 0)
            if self.callback is not None:
                self.callback()
