from typing import Any

import scrapy
from scrapy.http import Response

from weather_scrapy.spiders.WrappedRedisSpider import WrappedRedisSpider


class ForcastSpider(WrappedRedisSpider):

    def start_requests(self):
        request = self.start_requests()
        if request:
            for req in request:
                yield req
        else:
            self.start_forcast_scrape()


    def start_forcast_scrape(self):

        yield scrapy.Request(url=f'http://www.weather.com.cn/weather40d/{city_id}.shtml',
                             callback=self.parse_forcast)
        pass


    def parse_forcast(self, response: Response,) -> Any:
        pass