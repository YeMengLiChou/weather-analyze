# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WeatherScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class RealWeatherItem(scrapy.Item):
    """
    实时数据Item
    """
    # 城市中文`
    city_name = scrapy.Field()
    # 城市id`
    city_id = scrapy.Field()
    # 城市所属省份拼音
    city_province = scrapy.Field()

    # 当前温度`
    temp = scrapy.Field()
    # 白天温度`
    d_temp = scrapy.Field()
    # 夜晚温度`
    n_temp = scrapy.Field()
    # 湿度`
    humidity = scrapy.Field()
    # 风向`
    w_direction = scrapy.Field()
    # 风级`
    w_level = scrapy.Field()
    # 风速`
    w_speed = scrapy.Field()
    # 降水量
    rain = scrapy.Field()
    # 24小时降水量
    rain24h = scrapy.Field()
    # 空气质量
    aqi = scrapy.Field()
    # 天气描述`
    description = scrapy.Field()
    # 生活指数表述 `
    content = scrapy.Field()
    # 时间戳
    timestamp = scrapy.Field()
    # 日出日落时间
    sunrise = scrapy.Field()
    sunset = scrapy.Field()


class HistoryWeatherItem(scrapy.Item):
    # 城市中文`
    city_name = scrapy.Field()
    # 城市id`
    city_id = scrapy.Field()
    # 城市所属省份
    city_province = scrapy.Field()
    # 当前时间的时间戳
    timestamp = scrapy.Field()
    # 天气描述
    description = scrapy.Field()
    # 最高温度
    high_temp = scrapy.Field()
    # 最低温度
    low_temp = scrapy.Field()
    # 风向
    w_direction = scrapy.Field()
    # 风等级
    w_level = scrapy.Field()
    # aqi
    aqi = scrapy.Field()
    # aqi状态
    aqi_status = scrapy.Field()