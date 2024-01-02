import datetime
import json
import re
from typing import Any

from lxml import etree, html
import scrapy
from scrapy.http import Response
from scrapy.selector import SelectorList

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
                area_info_part = f"areaInfo%5BareaId%5D={54511}&areaInfo%5BareaType%5D={2}"
                date_part = f"date%5Byear%5D={now.year - year}&date%5Bmonth%5D={month}"
                urls.append(f'{url_prefix}?{area_info_part}&{date_part}')
        for month in range(1, now.month):
            area_info_part = f"areaInfo%5BareaId%5D={54511}&areaInfo%5BareaType%5D={2}"
            date_part = f"date%5Byear%5D={now.year}&date%5Bmonth%5D={month}"
            urls.append(f'{url_prefix}?{area_info_part}&{date_part}')
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
    def __parse_wind_info(wind_str: str) -> tuple[str | None, int | None]:
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
        ma = re.match(r'(.+)风\s*(\d+)级', wind_str)
        if not ma:
            ma = re.match(r'(.+)风(微风)', wind_str)
        if ma:
            wind_direction = ma.group(1)
            wind_level = ma.group(2)
            result = []
            for char in wind_direction:
                if char in en_directions:
                    result.append(en_directions[char])
            return ''.join(result), wind_level
        else:
            return None, None

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
            self.wait_scraping()
            yield from self.start_history_scrape()

    def start_history_scrape(self):
        """
        开始爬取天气
        :return:
        """
        self.logger.info('======> 开始爬取历史天气')
        all_cities: list[str] = self.redis.get_all_cities()
        all_cities_sp_id: list[str] = self.redis.get_cities_spid_by_name(all_cities)
        for city_id in all_cities_sp_id:
            for url in self.__get_scrape_urls(city_id):
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'city_id': city_id},
                    dont_filter=True
                )
                break
            break

    def parse(self, response: Response, **kwargs: Any) -> Any:
        text = response.text
        content = json.loads(text)
        data = content['data']
        resolved = html.fromstring(data)

        items = []
        rows = resolved.xpath('//table/tr')[1:]
        for row in rows:
            tds = row.xpath('./td')
            texts = SelectorList(tds[:-1]).xpath('./text()')

            timestamp = self.__get_timestamp_from_time_str(texts[0])
            high_temp = texts[1][:-1]
            low_temp = texts[2][:-1]
            description = texts[3]
            w_direction, w_level = self.__parse_wind_info(texts[4])

            aqi_text = tds[-1].xpath('./span/text()')[0]
            if aqi_text == '-':
                aqi = None
                aqi_status = None
            else:
                aqi, aqi_status = aqi_text.split()
                aqi = int(aqi)

            item = HistoryWeatherItem()
            city_id = response.meta['city_id']
            city_name = self.redis.get_city_name_by_spid(city_id)
            item['city_name'] = city_name
            item['city_id'] = city_id
            item['city_province'] = self.redis.get_city_province(city_name)
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
