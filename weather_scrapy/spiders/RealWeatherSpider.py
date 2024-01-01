import datetime
import json
import time
from typing import Any

import scrapy
from scrapy.http import Response

from weather_scrapy.items import RealWeatherItem
from weather_scrapy.spiders.WrappedRedisSpider import WrappedRedisSpider


class RealWeatherSpider(WrappedRedisSpider):
    name = 'real'

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.131 Safari/537.36',
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "proxy-connection": "keep-alive",
        "referer": 'http://www.weather.com.cn/',
    }

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
        print('====> request:' + str(request))
        if request:
            yield from request
        else:
            self.wait_scraping()
            yield from self.start_real_scrape()

    def start_real_scrape(self):
        """
        开始爬取天气
        :return:
        """
        self.logger.info('======> 开始爬取天气')
        all_cities: list[str] = self.redis.get_all_cities()
        ids = self.redis.get_cities_id(all_cities)
        for city_name, city_id in zip(all_cities, ids):
            yield scrapy.Request(
                url=f'http://www.weather.com.cn/weather1d/{city_id}.shtml',
                callback=self.parse_page,
                meta={
                    'city_id': city_id,
                    'city_name': city_name
                },
                dont_filter=True
            )
            break

    def parse_page(self, response: Response) -> Any:
        """
        解析网页
        :param response:
        :return:
        """
        meta = response.meta
        city_id = meta['city_id']
        city_name = meta['city_name']
        print(f'=====> {city_id} {city_name}')

        sunrise = response.xpath('//p[@class="sun sunUp"]/span/text()').get()[-5:]
        sunset = response.xpath('//p[@class="sun sunDown"]/span/text()').get()[-5:]

        def get_timestamp_from_time_str(time_str: str) -> int:
            """
            获取时间戳
            :param time_str:
            :return:
            """
            data = time_str.split(':')
            now = datetime.datetime.now()
            return int(datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=int(data[0]),
                minute=int(data[1]),
            ).timestamp() * 1000)

        # 日出日落的时间戳
        meta['sunrise'] = get_timestamp_from_time_str(sunrise)
        meta['sunset'] = get_timestamp_from_time_str(sunset)

        # 生活指数内容
        live_content = response.xpath('//div[@class="livezs"]//ul[@class="clearfix"]//li')
        content = {}
        for item in live_content:
            key = item.xpath('./em/text()').get()
            description = item.xpath('./p/text()').get()
            status = item.xpath('./span/text()').get()
            if key:
                content[key] = {
                    'status': status,
                    'description': description
                }
        json_content = json.dumps(content, ensure_ascii=False)
        meta['content'] = json_content

        yield scrapy.Request(
            url=f'http://d1.weather.com.cn/dingzhi/{city_id}.html?_={int(time.time() * 1000)}',
            callback=self.parse_weather_simple_info,
            meta=meta,
            headers=self.header,
            dont_filter=True
        )

    def parse_weather_simple_info(self, response: Response) -> Any:
        """
        解析天气简要信息
        :param response:
        :return:
        """
        text = response.text
        meta = response.meta

        first_brace_index = text.find('{')
        first_semicolon_index = text.find(';')
        json_content = text[first_brace_index:first_semicolon_index]
        content = json.loads(json_content)['weatherinfo']

        # 白天夜晚的温度
        meta['d_temp'] = content['temp'][:-1]  # 去掉后面的%
        meta['n_temp'] = content['tempn'][:-1]
        meta['description'] = content['weather']
        meta['city_name'] = content['cityname']

        yield scrapy.Request(
            url=f'http://d1.weather.com.cn/sk_2d/{meta["city_id"]}.html?_={int(time.time() * 1000)}',
            callback=self.parse_weather_detail_info,
            meta=meta,
            headers=self.header,
            dont_filter=True
        )

    def parse_weather_detail_info(self, response: Response) -> Any:
        """
        解析天气详情
        :param response:
        :return:
        """
        text = response.text
        meta = response.meta

        first_brace_index = text.find('{')
        last_brace_index = text.rfind('}')
        json_content = text[first_brace_index:last_brace_index + 1]
        content = json.loads(json_content)

        meta['temp'] = content['temp']
        meta['w_level'] = content['WS']  # 风级

        speed = int(content['wse'].replace('km/h', ''))
        meta['w_speed'] = speed  # 风速

        meta['w_direction'] = content['wde']  # 风向

        level = int(content['WS'].replace('级', ''))
        meta['w_level'] = level

        humidity = int(content['SD'].replace('%', ''))
        meta['humidity'] = humidity

        meta['aqi'] = content['aqi']

        meta['rain'] = int(content['rain'])
        meta['rain24h'] = int(content['rain24h'])

        _time = content['time']
        meta['timestamp'] = int(datetime.datetime(
            year=datetime.datetime.now().year,
            month=datetime.datetime.now().month,
            day=datetime.datetime.now().day,
            hour=int(_time.split(':')[0]),
            minute=int(_time.split(':')[1]),
        ).timestamp() * 1000)

        item = RealWeatherItem()
        item['city_id'] = meta['city_id']
        item['city_name'] = meta['city_name']
        item['city_province'] = self.redis.get_city_id(
            self.redis.get_city_province(meta['city_name'])
        )
        item['temp'] = meta['temp']
        item['d_temp'] = meta['d_temp']
        item['n_temp'] = meta['n_temp']
        item['w_level'] = meta['w_level']
        item['w_speed'] = meta['w_speed']
        item['w_direction'] = meta['w_direction']
        item['humidity'] = meta['humidity']
        item['description'] = meta['description']
        item['content'] = meta['content']
        item['timestamp'] = meta['timestamp']
        item['aqi'] = meta['aqi']
        item['rain'] = meta['rain']
        item['rain24h'] = meta['rain24h']
        item['sunrise'] = meta['sunrise']
        item['sunset'] = meta['sunset']

        yield item
