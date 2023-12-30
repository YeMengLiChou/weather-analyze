from typing import Any

from scrapy.http import Response

from weather_scrapy.spiders.WrappedRedisSpider import WrappedRedisSpider


class RealWeatherSpider(WrappedRedisSpider):
    name = 'real'

    allowed_domains = ['tianqi.2345.com']

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
        for req in request:
            yield req

    def start_real_scrape(self):
        self.logger.info('======> 开始爬取天气')

        pass

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass
