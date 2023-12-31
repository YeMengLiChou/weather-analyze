from typing import Generator
from typing import Any

import scrapy

from config import constants
from scrapy.http import Response

from weather_scrapy.spiders.WrappedRedisSpider import WrappedRedisSpider


class RealWeatherSpider(WrappedRedisSpider):
    name = 'real'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        instance = cls(crawler.settings.get('REDIS_CONFIG'), **kwargs)
        instance._set_crawler(crawler)
        return instance

    def start_requests(self):
        """
        开始爬取
        :return:
        """
        # 开始准备工作，检查是否存在城市数据
        request = self.start_prepare(callback=self.start_real_scrape)
        if request:
            for req in request:
                yield req
        else:
            yield self.start_real_scrape()

    def start_real_scrape(self):
        """
        开始爬取天气
        :return:
        """
        self.logger.info('======> 开始爬取天气')
        all_cities: list[str] = self.redis.get_all_cities()
        ids = self.redis.get_cities_id(all_cities)
        for idx, city_id in zip(all_cities, ids):
            yield scrapy.Request(url=f'http://www.weather.com.cn/weather1d/{city_id}.shtml',
                                 callback=self.parse)
            yield scrapy.Request(url=f'http://www.weather.com.cn/weather40d/{city_id}.shtml',
                                 callback=self.parse_forcast)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass

    def parse_forcast(self, response: Response, **kwargs: Any) -> Any:
        pass
