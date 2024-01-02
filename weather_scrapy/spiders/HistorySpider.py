import datetime
import json
import re
from typing import Any

import scrapy
from lxml import html
from scrapy.http import Response
from scrapy.selector import SelectorList

from weather_scrapy.items import HistoryWeatherItem
from weather_scrapy.spiders.WrappedRedisSpider import WrappedRedisSpider


class HistorySpider(WrappedRedisSpider):
    name = 'history'

    def __get_scrape_urls(self, city_name: str) -> list:
        """
        获取历史天气的url
        :param city_name:
        :return:
        """
        url_prefix = f"https://tianqi.2345.com/Pc/GetHistory"
        now = datetime.datetime.now()
        urls = []

        dates = [(year, month) for year in range(now.year - 5, now.year) for month in range(1, 13)]
        for month in range(1, now.month):
            dates.append((now.year, month))
        need_dates = []
        for year, month in dates:
            if not self.redis.is_exist_history_date(city_name, f'{year}{month}'):
                need_dates.append((year, month))
        for year, month in need_dates:
            area_info_part = f"areaInfo%5BareaId%5D={city_name}&areaInfo%5BareaType%5D=2"
            date_part = f"date%5Byear%5D={year}&date%5Bmonth%5D={month}"
            urls.append((f'{url_prefix}?{area_info_part}&{date_part}', year, month))
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
            if wind_level == '微风':
                wind_level = 0
            else:
                wind_level = int(wind_level)
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
            for url, year, month in self.__get_scrape_urls(city_id):
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'city_id': city_id, 'year': year, 'month': month},
                    dont_filter=True
                )
            #     break
            # break

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """
        解析历史数据页面
        :param response:
        :param kwargs:
        :return:
        """
        text = response.text
        content = json.loads(text)
        data = content['data']
        resolved = html.fromstring(data)
        meta = response.meta
        self.logger.info(f'======> history: {meta["city_id"]} {meta["year"]}-{meta["month"]}')
        items = []
        rows = resolved.xpath('//table//tr')[1:]
        for row in rows:
            tds = row.xpath('./td')
            pos = len(tds)
            if pos == 6:
                texts = SelectorList(tds[:-1]).xpath('./text()')
            else:
                texts = SelectorList(tds).xpath('./text()')

            timestamp = self.__get_timestamp_from_time_str(texts[0])
            high_temp = int(texts[1][:-1])
            low_temp = int(texts[2][:-1])
            description = texts[3]
            w_direction, w_level = self.__parse_wind_info(texts[4])
            if pos == 6:
                aqi_text = tds[-1].xpath('./span/text()')[0]
                if aqi_text == '-':
                    aqi = None
                    aqi_status = None
                else:
                    aqi, aqi_status = aqi_text.split()
                    aqi = int(aqi)
            else:
                aqi = None
                aqi_status = None
            item = HistoryWeatherItem()
            city_id = meta['city_id']
            city_name = self.redis.get_city_name_by_spid(city_id)
            item['city_name'] = city_name
            item['city_id'] = self.redis.get_city_id(city_name)
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
        self.redis.add_history_date(response.meta['city_id'], f'{response.meta["year"]}{response.meta["month"]}')
