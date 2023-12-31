from typing import Any

import scrapy
from requests import Response

from weather_scrapy.spiders.WrappedRedisSpider import WrappedRedisSpider


class HistorySpider(WrappedRedisSpider):
    name = 'history'

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
            yield from request
        else:
            yield from self.start_real_scrape()

    def start_real_scrape(self):
        """
        开始爬取天气
        :return:
        """
        self.logger.info('======> 开始爬取天气')
        all_cities: list[str] = self.redis.get_all_cities()
        ids = self.redis.get_cities_id(all_cities)
        for idx, city_id in zip(all_cities, ids):
            yield scrapy.Request(url='http://www.weather.com.cn/weather1d/101300501.shtml')

        # for city in all_cities:
        #     yield scrapy.Request(url=)
        pass

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass
