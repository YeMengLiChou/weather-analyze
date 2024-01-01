import datetime
import json
from typing import Any

from lxml import etree
import scrapy
from scrapy.http import Response

from weather_scrapy.items import HistoryWeatherItem
from weather_scrapy.spiders.WrappedRedisSpider import WrappedRedisSpider


class HistorySpider(WrappedRedisSpider):
    name = 'history'

    @staticmethod
    def __get_scrape_urls(city_name: str) -> list[str]:
        """
        获取历史天气的url
        :param city_name:
        :return:
        """
        url_prefix = f"https://tianqi.2345.com/Pc/GetHistory"
        now = datetime.datetime.now()
        urls = []
        for year in range(1, 6):
            for month in range(1, 12):
                area_info_part = f"areaInfo[areaId]={54511}&areaInfo[areaType]={2}"
                date_part = f"date[year]={now.year - year}&date[month]={month}"
                urls.append(f'{url_prefix}?{area_info_part}&{date_part}.html')
        for month in range(1, now.month):
            area_info_part = f"areaInfo[areaId]={54511}&areaInfo[areaType]={2}"
            date_part = f"date[year]={now.year}&date[month]={month}"
            urls.append(f'{url_prefix}?{area_info_part}&{date_part}.html')
        return urls

    @staticmethod
    def __get_timestamp_from_time_str(time_str: str) -> int:
        """
        获取时间戳
        :param time_str: xxxx-xx-xx 星期x
        :return:
        """
        date = time_str.split()[0]
        parts = date.split('-')
        return int(datetime.datetime(
            year=int(parts[0]),
            month=int(parts[1]),
            day=int(parts[2])
        ).timestamp() * 1000)

    @staticmethod
    def __parse_wind_info(wind_str: str) -> tuple[str, int]:
        """
        将中文的风向转为英文表示，同时返回风级
        :param wind_str:
        :return:
        """
        en_directions = {
            '西': 'W',
            '东': 'E',
            '北': 'N',
            '南': 'S'
        }
        winds = wind_str.split('风')
        wind_direction = winds[0]
        wind_level = winds[1][:-1]  # 去掉'级'
        result = []
        for char in wind_direction:
            if char in en_directions:
                result.append(en_directions[char])
        return ''.join(result), int(wind_level)

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
        request = self.start_prepare(callback=self.start_history_scrape)
        if request:
            yield from request
        else:
            yield from self.start_history_scrape()

    def start_history_scrape(self):
        """
        开始爬取天气
        :return:
        """
        self.logger.info('======> 开始爬取历史天气')
        all_cities: list[str] = self.redis.get_all_cities()
        for city in all_cities:
            for url in self.__get_scrape_urls(city):
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'city_name': city}
                )
                break
            break

    def parse(self, response: Response, **kwargs: Any) -> Any:
        text = response.text
        content = json.loads(text)
        data = content['data']
        resolved = etree.HTML(data, 'html.parser')

        items = []
        rows = resolved.xpath('/table/tr')[1:]
        for row in rows:
            tds = row.xpath('./td')
            texts = tds[:-1].xpath('./text()')

            timestamp = self.__get_timestamp_from_time_str(texts[0])
            high_temp = texts[1][:-1]
            low_temp = texts[2][:-1]
            description = texts[3]
            w_direction, w_level = self.__parse_wind_info(texts[4])

            aqi_text = tds[-1].xpath('./span/text()').get()
            aqi, aqi_status = aqi_text.split(' ')

            item = HistoryWeatherItem()
            city_pinyin = response.meta['city_name']
            city_name = self.redis.get_city_chinese(city_pinyin)
            item['city_name'] = city_name
            item['city_pinyin'] = city_pinyin
            item['city_id'] = self.redis.get_city_id(city_pinyin)
            item['city_province'] = self.redis.get_city_province(city_pinyin)
            item['timestamp'] = timestamp
            item['description'] = description
            item['high_temp'] = high_temp
            item['low_temp'] = low_temp
            item['w_direction'] = w_direction
            item['w_level'] = w_level
            item['aqi'] = aqi
            item['aqi_status'] = aqi_status
            items.append(item)
        yield from items
